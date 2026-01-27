'use client';

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
    Accordion,
    AccordionContent,
    AccordionItem,
    AccordionTrigger,
} from "@/components/ui/accordion";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select"
import { Input } from "@/components/ui/input"

import { CsvUploader } from './CsvUploader';
import { DataPreview } from './DataPreview';
import { SchemaView } from './SchemaView';
import { getCsvSchema, getCsvData, suggestChart, planChart } from '../api/charts';
import { ChartArea } from './ChartArea';
import { ChartConfig, ChartPlan } from '../types';
import { processDataForChart, getPreviewData } from '../utils/dataProcessing';

export const ChartsWorkspace = () => {
    const [csvId, setCsvId] = useState<string | null>(null);
    const [previewData, setPreviewData] = useState<any[]>([]);
    const [schema, setSchema] = useState<Record<string, string>>({});
    const [selectedChartType, setSelectedChartType] = useState<string>('');
    const [userQuery, setUserQuery] = useState('');
    const [isSuggesting, setIsSuggesting] = useState(false);
    const [suggestedChartTypes, setSuggestedChartTypes] = useState<string[]>([]);
    const [charts, setCharts] = useState<ChartConfig[]>([]);
    const [isAddingChart, setIsAddingChart] = useState(false);

    const handleUploadSuccess = async (id: string) => {
        setCsvId(id);
        setSuggestedChartTypes([]); // Reset suggestions on new upload
        setSelectedChartType('');
        try {
            // Fetch Schema
            const schemaRes = await getCsvSchema(id);
            setSchema(schemaRes.schema);

            // Fetch Data for preview (using danfo.js)
            const csvText = await getCsvData(id);
            const data = await getPreviewData(csvText);
            setPreviewData(data);

        } catch (error) {
            console.error("Error fetching data/schema", error);
        }
    };

    const handleSuggestChart = async () => {
        if (!csvId || !userQuery) return;
        setIsSuggesting(true);
        setSuggestedChartTypes([]);
        setSelectedChartType('');

        let accumulatedJson = '';

        try {
            await suggestChart({
                columns: schema,
                user_query: userQuery,
                csv_id: csvId
            }, (chunk) => {
                accumulatedJson += chunk;
            });

            // Attempt to parse the final JSON
            try {
                // The backend streams data chunks. If the agent returns a pure JSON object,
                // accumulatedJson should be that object string.
                // However, sometime agents output "Here is the json: {...}".
                // But chart_suggester_agent uses output_schema properly, so it should be just JSON.
                // We might need to find the first '{' and last '}' if there is noise.
                const firstBrace = accumulatedJson.indexOf('{');
                const lastBrace = accumulatedJson.lastIndexOf('}');

                if (firstBrace !== -1 && lastBrace !== -1) {
                    const jsonStr = accumulatedJson.substring(firstBrace, lastBrace + 1);
                    const parsed = JSON.parse(jsonStr);
                    if (parsed.chart_types && Array.isArray(parsed.chart_types)) {
                        setSuggestedChartTypes(parsed.chart_types);
                        if (parsed.chart_types.length > 0) {
                            setSelectedChartType(parsed.chart_types[0]);
                        }
                    }
                }
            } catch (e) {
                console.error("Failed to parse agent response", e);
            }

        } catch (error) {
            console.error("Error suggesting chart", error);
        } finally {
            setIsSuggesting(false);
        }
    };

    const handleAddChart = async () => {
        if (!csvId || !selectedChartType || !userQuery) return;
        setIsAddingChart(true);
        try {
            // 1. Get Plan
            let accumulatedJson = '';
            await planChart({
                chart_type: selectedChartType.toLowerCase().includes('bar') ? 'bar' : selectedChartType,
                columns: schema,
                user_query: userQuery
            }, (chunk) => {
                accumulatedJson += chunk;
            });

            // Parse Plan
            let plan: ChartPlan | null = null;
            try {
                // The backend uses SSE for plan too
                const firstBrace = accumulatedJson.indexOf('{');
                const lastBrace = accumulatedJson.lastIndexOf('}');
                if (firstBrace !== -1 && lastBrace !== -1) {
                    const jsonStr = accumulatedJson.substring(firstBrace, lastBrace + 1);
                    plan = JSON.parse(jsonStr);
                }
            } catch (e) {
                console.error("Failed to parse plan", e);
            }

            if (plan && plan.type === 'bar') {
                // 2. Fetch Full Data
                const csvText = await getCsvData(csvId);

                // 3. Process Data
                const newChart = await processDataForChart(
                    csvText,
                    plan,
                    Date.now().toString(),
                    `${userQuery} (${selectedChartType})`
                );

                setCharts(prev => [...prev, newChart]);
            }

        } catch (error) {
            console.error("Failed to add chart", error);
        } finally {
            setIsAddingChart(false);
        }
    };

    return (
        <div className="w-full max-w-5xl mx-auto p-4 space-y-6">
            <Card>
                <CardContent className="p-6">
                    <CsvUploader onUploadSuccess={handleUploadSuccess} />
                </CardContent>
            </Card>

            {csvId && (
                <>
                    <Card>
                        <CardHeader>
                            <CardTitle>Data Overview</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <Accordion type="single" collapsible defaultValue="preview" className="w-full">
                                <AccordionItem value="preview">
                                    <AccordionTrigger>Preview Accordion</AccordionTrigger>
                                    <AccordionContent>
                                        <DataPreview data={previewData} />
                                    </AccordionContent>
                                </AccordionItem>
                                <AccordionItem value="schema">
                                    <AccordionTrigger>Schema Accordion</AccordionTrigger>
                                    <AccordionContent>
                                        <SchemaView schema={schema} />
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        </CardContent>
                    </Card>

                    <Card>
                        <CardContent className="p-6">
                            <div className="flex flex-col gap-4">
                                <div className="flex gap-4">
                                    <Input
                                        placeholder="Describe what you want to visualize (e.g., 'Show sales by region')"
                                        value={userQuery}
                                        onChange={(e) => setUserQuery(e.target.value)}
                                    />
                                    <Button
                                        variant="secondary"
                                        onClick={handleSuggestChart}
                                        disabled={isSuggesting || !userQuery}
                                    >
                                        {isSuggesting ? "Thinking..." : "Suggest Chart"}
                                    </Button>
                                </div>

                                <div className="flex gap-4 items-end">
                                    <div className="flex-1">
                                        <Select
                                            value={selectedChartType}
                                            onValueChange={setSelectedChartType}
                                            disabled={suggestedChartTypes.length === 0}
                                        >
                                            <SelectTrigger className="w-full">
                                                <SelectValue placeholder={suggestedChartTypes.length === 0 ? "Ask for suggestions..." : "Select chart type"} />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {suggestedChartTypes.map((type) => (
                                                    <SelectItem key={type} value={type}>
                                                        {type}
                                                    </SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                    <Button
                                        onClick={handleAddChart}
                                        disabled={!selectedChartType || isAddingChart}
                                    >
                                        {isAddingChart ? "Adding..." : "Add Chart"}
                                    </Button>
                                </div>
                            </div>
                        </CardContent>
                    </Card>

                    <ChartArea charts={charts} />
                </>
            )}
        </div>
    );
};
