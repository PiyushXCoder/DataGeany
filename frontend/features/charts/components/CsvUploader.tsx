'use client';

import React, { useRef, useState } from 'react';
import { Button } from "@/components/ui/button";
import { uploadCsv } from "../api/charts";

interface CsvUploaderProps {
    onUploadSuccess: (csvId: string) => void;
}

export const CsvUploader: React.FC<CsvUploaderProps> = ({ onUploadSuccess }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [fileName, setFileName] = useState<string | null>(null);

    const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            setFileName(file.name);
            setIsUploading(true);
            try {
                const response = await uploadCsv(file);
                onUploadSuccess(response.csvId);
            } catch (error) {
                console.error("Upload failed", error);
                // Could add toast notification here
            } finally {
                setIsUploading(false);
            }
        }
    };

    const handleBrowseClick = () => {
        fileInputRef.current?.click();
    };

    return (
        <div className="flex items-center gap-4 p-4 border rounded-md">
            <span className="font-medium">Choose csv file</span>
            <div className="flex items-center gap-2">
                <Button variant="outline" onClick={handleBrowseClick} disabled={isUploading}>
                    {isUploading ? "Uploading..." : "browse"}
                </Button>
                {fileName && <span className="text-sm text-gray-500">{fileName}</span>}
            </div>
            <input
                type="file"
                accept=".csv"
                ref={fileInputRef}
                className="hidden"
                onChange={handleFileChange}
            />
        </div>
    );
};
