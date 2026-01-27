'use client';

import React from 'react';
import { ChartCard } from './ChartCard';
import { ChartConfig } from '../types';

interface ChartAreaProps {
    charts: ChartConfig[];
}

export const ChartArea: React.FC<ChartAreaProps> = ({ charts }) => {
    return (
        <div className="grid grid-cols-1 gap-6">
            {charts.length === 0 ? (
                <div className="col-span-full min-h-[400px] border rounded-lg p-8 flex items-center justify-center bg-gray-50 text-gray-400">
                    Your charts will appear here.
                </div>
            ) : (
                charts.map((chart) => (
                    <ChartCard
                        key={chart.id}
                        title={chart.title}
                        chartData={chart.data}
                        chartType={chart.type}
                    />
                ))
            )}
        </div>
    );
};
