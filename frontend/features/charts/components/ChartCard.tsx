'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend
);

interface ChartCardProps {
    title: string;
    chartData: any;
    chartType: string;
}

export const ChartCard: React.FC<ChartCardProps> = ({ title, chartData, chartType }) => {
    return (
        <Card className="w-full h-full min-h-[300px]">
            <CardHeader>
                <CardTitle>{title}</CardTitle>
            </CardHeader>
            <CardContent>
                {chartType === 'bar' && (
                    <Bar options={{ responsive: true, maintainAspectRatio: false }} data={chartData} />
                )}
            </CardContent>
        </Card>
    );
};
