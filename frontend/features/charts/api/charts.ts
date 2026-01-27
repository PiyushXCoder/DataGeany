import api from '@/lib/axios';
import { CsvUploadResponse, CsvSchemaResponse, ChartSuggestionRequest } from '../types';

export const uploadCsv = async (file: File): Promise<CsvUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/charts/csv', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getCsvSchema = async (csvId: string): Promise<CsvSchemaResponse> => {
    const response = await api.get(`/charts/csv/${csvId}/schema`);
    return response.data;
};

// Added method to get CSV data for preview
export const getCsvData = async (csvId: string): Promise<string> => {
    const response = await api.get(`/charts/csv/${csvId}`, {
        responseType: 'text'
    });
    return response.data;
}

// SSE usually handled in component via EventSource or fetch, but keeping a reference here
export const getSuggestChartsUrl = () => `${api.defaults.baseURL}/charts/suggest`;

export const suggestChart = async (
    payload: ChartSuggestionRequest,
    onChunk: (chunk: string) => void
) => {
    const response = await fetch(`${api.defaults.baseURL}/charts/suggest`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });

    if (!response.body) {
        throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value);
        // Basic SSE parsing
        const lines = chunk.split('\n');
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data && data !== '[DONE]') {
                    onChunk(data);
                }
            }
        }
    }
};
