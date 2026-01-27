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
