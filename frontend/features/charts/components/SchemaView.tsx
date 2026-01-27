'use client';

import React from 'react';
import { ScrollArea } from "@/components/ui/scroll-area";

interface SchemaViewProps {
    schema: Record<string, string>;
}

export const SchemaView: React.FC<SchemaViewProps> = ({ schema }) => {
    if (!schema || Object.keys(schema).length === 0) {
        return <div className="p-4 text-center text-gray-500">No schema available.</div>;
    }

    return (
        <div className="rounded-md border h-[200px]">
            <ScrollArea className="h-full w-full p-4">
                <div className="grid grid-cols-2 gap-4">
                    {Object.entries(schema).map(([col, type]) => (
                        <div key={col} className="flex justify-between p-2 border rounded hover:bg-gray-50">
                            <span className="font-semibold">{col}</span>
                            <span className="text-gray-600 bg-gray-100 px-2 py-0.5 rounded text-sm">{type}</span>
                        </div>
                    ))}
                </div>
            </ScrollArea>
        </div>
    );
};
