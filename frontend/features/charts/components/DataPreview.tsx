'use client';

import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

interface DataPreviewProps {
    data: Record<string, any>[];
}

export const DataPreview: React.FC<DataPreviewProps> = ({ data }) => {
    if (!data || data.length === 0) {
        return <div className="p-4 text-center text-gray-500">No data available for preview.</div>;
    }

    const headers = Object.keys(data[0]);

    return (
        <div className="rounded-md border h-[300px]">
            <ScrollArea className="h-full w-full">
                <Table>
                    <TableHeader>
                        <TableRow>
                            {headers.map((header) => (
                                <TableHead key={header}>{header}</TableHead>
                            ))}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {data.map((row, index) => (
                            <TableRow key={index}>
                                {headers.map((header) => (
                                    <TableCell key={`${index}-${header}`}>{row[header]}</TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
                <ScrollBar orientation="horizontal" />
            </ScrollArea>
        </div>
    );
};
