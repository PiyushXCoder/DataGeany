import * as dfd from 'danfojs';
import { ChartPlan, ChartConfig } from '../types';

export const processDataForChart = async (
    csvText: string,
    plan: ChartPlan,
    chartId: string,
    title: string
): Promise<ChartConfig> => {
    // 1. Create DataFrame
    // danfojs read_csv mostly expects file path or URL in node/browser, 
    // but readCSV can also take a Blob/File or standard CSV string if configured.
    // However, read_csv is async.
    // A simpler way for string CSV is to parse it to JSON array first or use readCSV with a Blob.

    // For simplicity, let's create a temporary blob
    const blob = new Blob([csvText], { type: 'text/csv' });
    const file = new File([blob], "temp.csv", { type: "text/csv" });

    const df = await dfd.readCSV(file);

    // 2. Pre-process: Filter columns and ensure numeric type for aggregation
    let subDf = df.loc({ columns: [plan.x.column, plan.y.column] });

    // Explicitly cast Y column to float using manual mapping
    const colName = plan.y.column;
    // @ts-ignore
    const rawValues = subDf[colName].values;
    const castedValues = rawValues.map((v: any) => parseFloat(v));
    const castedSeries = new dfd.Series(castedValues);
    subDf.addColumn(colName, castedSeries, { inplace: true });

    // 3. Group and Aggregate
    let grp = subDf.groupby([plan.x.column]);
    let aggDf: dfd.DataFrame;

    if (plan.y.aggregation === 'sum') {
        aggDf = grp.sum();
    } else if (plan.y.aggregation === 'avg') {
        aggDf = grp.mean();
    } else if (plan.y.aggregation === 'count') {
        aggDf = grp.count();
    } else {
        aggDf = grp.sum(); // Default
    }

    // The aggregation column name often changes, e.g., "sales_sum"
    // We need to find the column that matches.
    const yColName = `${plan.y.column}_${plan.y.aggregation}`;
    // Or sometimes danfo just uses the same name if it can. 
    // Let's inspect columns or assume standard naming "col_sum"

    // Actually danfo.js grouping results usually have columns like `col_sum`.
    // Let's protect against column naming nuances by checking available columns.
    const availableCols = aggDf.columns;
    let finalYCol = availableCols.find(c => c.startsWith(plan.y.column) || c.endsWith(plan.y.aggregation));
    if (!finalYCol) finalYCol = availableCols[1]; // Fallback to 2nd column (1st is usually index/group)

    // 3. Sort and Limit
    aggDf.sortValues(finalYCol, { ascending: false, inplace: true });
    const topDf = aggDf.head(plan.top_k);

    // 4. Extract data for Chart.js
    // x-axis labels
    const labels = topDf[plan.x.column].values;
    // y-axis data
    const dataValues = topDf[finalYCol].values;

    const chartData = {
        labels: labels,
        datasets: [
            {
                label: plan.y.label,
                data: dataValues,
                backgroundColor: 'rgba(53, 162, 235, 0.5)',
                borderColor: 'rgb(53, 162, 235)',
                borderWidth: 1,
            },
        ],
    };

    return {
        id: chartId,
        title: title,
        type: plan.type,
        data: chartData,
    };
};

export const getPreviewData = async (csvText: string, limit: number = 5): Promise<any[]> => {
    const blob = new Blob([csvText], { type: 'text/csv' });
    const file = new File([blob], "temp.csv", { type: "text/csv" });
    const df = await dfd.readCSV(file);
    const previewDf = df.head(limit);
    return dfd.toJSON(previewDf) as any[];
};
