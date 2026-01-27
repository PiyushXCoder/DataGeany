export interface CsvUploadResponse {
    status: string;
    message: string;
    csvId: string;
}

export interface CsvSchemaResponse {
    csvId: string;
    schema: Record<string, string>;
}

export interface ChartSuggestionRequest {
    columns: Record<string, string>;
    user_query: string;
    csv_id?: string;
}

export interface PlanChartRequest {
    chart_type: string;
    columns: Record<string, string>;
    user_query: string;
}

export interface XAxis {
    column: string;
    label: string;
}

export interface YAxis {
    column: string;
    aggregation: 'sum' | 'avg' | 'count';
    label: string;
}

export interface ChartPlan {
    type: 'bar';
    x: XAxis;
    y: YAxis;
    top_k: number;
}

export interface ChartConfig {
    id: string;
    title: string;
    type: string;
    data: any; // Chart.js data structure
}
