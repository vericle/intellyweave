"use client";

import React, { useEffect, useState } from "react";
import { AggregationPayload } from "@/app/types/displays";
import DataTable from "@/app/components/explorer/DataTable";

interface AggregationDisplayProps {
  aggregation: AggregationPayload[];
}

interface TableData {
  header: { [key: string]: string };
  /* eslint-disable @typescript-eslint/no-explicit-any */
  data: { [key: string]: any }[];
}

interface TableDataPerField {
  [key: string]: TableData;
}

interface CollectionData {
  [collectionName: string]: TableDataPerField;
}

const AggregationDisplay: React.FC<AggregationDisplayProps> = ({
  aggregation,
}) => {
  const [collectionData, setCollectionData] = useState<CollectionData>({});

  const shouldDisplayColumn = (columnKey: string): boolean => {
    if (!columnKey) return false;
    if (columnKey.startsWith("_")) return false;
    if (columnKey === columnKey.toUpperCase()) return false;
    return true;
  };

  const isColumnEmpty = (
    /* eslint-disable @typescript-eslint/no-explicit-any */
    data: { [key: string]: any }[],
    columnKey: string
  ): boolean => {
    return data.every((row) => {
      const value = row[columnKey];
      return (
        value === null || value === undefined || value === 0 || value === ""
      );
    });
  };

  const reorderColumnsWithZerosLast = (
    header: { [key: string]: string },
    /* eslint-disable @typescript-eslint/no-explicit-any */
    data: { [key: string]: any }[]
  ): { [key: string]: string } => {
    const nonZeroColumns: { [key: string]: string } = {};
    const zeroColumns: { [key: string]: string } = {};

    for (const [key, type] of Object.entries(header)) {
      if (isColumnEmpty(data, key)) {
        zeroColumns[key] = type;
      } else {
        nonZeroColumns[key] = type;
      }
    }

    // Return non-zero columns first, then zero columns
    return { ...nonZeroColumns, ...zeroColumns };
  };

  const createTableDataPerCollection = (aggregation: AggregationPayload[]) => {
    const collectionData: CollectionData = {};

    for (const payload of aggregation) {
      for (const _collection of payload.collections) {
        for (const [collectionName, collection] of Object.entries(
          _collection
        )) {
          // Initialize collection data if it doesn't exist
          if (!collectionData[collectionName]) {
            collectionData[collectionName] = {};
          }

          for (const [fieldName, field] of Object.entries(collection)) {
            // Initialize table data for this field if it doesn't exist
            if (!collectionData[collectionName][fieldName]) {
              collectionData[collectionName][fieldName] = {
                header: {},
                data: [],
              };
            }

            // Create a map to store rows by field value to avoid duplicates
            const rowMap = new Map();
            // Track all columns in order: field name first, then groups (inverted), then main aggregations
            const columnOrder: string[] = [];
            const headers: { [key: string]: string } = {};

            // Process each aggregation value
            for (const aggValue of field.values) {
              const fieldValue = aggValue.field || "null";

              // Get or create row for this field value
              if (!rowMap.has(fieldValue)) {
                rowMap.set(fieldValue, {
                  [fieldName]: fieldValue,
                });
              }

              const row = rowMap.get(fieldValue);

              // Add the aggregation value
              if (shouldDisplayColumn(aggValue.aggregation)) {
                row[aggValue.aggregation] = aggValue.value;
              }

              // Track column order and headers
              if (
                shouldDisplayColumn(aggValue.aggregation) &&
                !headers[aggValue.aggregation]
              ) {
                headers[aggValue.aggregation] = "number";
              }

              // Process groups if they exist for this field value
              if (
                field.groups &&
                aggValue.field &&
                field.groups[aggValue.field]
              ) {
                const groupData = field.groups[aggValue.field];

                for (const [groupFieldName, groupField] of Object.entries(
                  groupData
                )) {
                  for (const groupValue of groupField.values) {
                    const columnName = `${groupFieldName}_${groupValue.aggregation}`;
                    if (shouldDisplayColumn(columnName)) {
                      row[columnName] = groupValue.value;

                      // Track group column headers
                      if (!headers[columnName]) {
                        headers[columnName] = groupField.type;
                      }
                    }
                  }
                }
              }
            }

            // Add field name column to header
            if (shouldDisplayColumn(fieldName)) {
              headers[fieldName] = field.type;
            }

            // Convert map values to array
            const dataArray = Array.from(rowMap.values());

            // Create ordered column list: field name first, then group columns (inverted), then main aggregations
            const groupColumns: string[] = [];
            const mainColumns: string[] = [];

            for (const key of Object.keys(headers)) {
              if (key === fieldName) {
                // Field name column goes first
                continue;
              } else if (key.includes("_")) {
                // Group columns
                groupColumns.push(key);
              } else {
                // Main aggregation columns
                mainColumns.push(key);
              }
            }

            // Invert group columns order so most important (top nested values) appear leftmost
            groupColumns.reverse();

            // Build final column order
            columnOrder.push(fieldName, ...groupColumns, ...mainColumns);

            // Create ordered header object
            const orderedHeader: { [key: string]: string } = {};
            for (const key of columnOrder) {
              if (headers[key] && shouldDisplayColumn(key)) {
                orderedHeader[key] = headers[key];
              }
            }

            // Reorder columns so zero-value columns appear last
            const reorderedHeader = reorderColumnsWithZerosLast(
              orderedHeader,
              dataArray
            );

            collectionData[collectionName][fieldName] = {
              header: reorderedHeader,
              data: dataArray,
            };
          }
        }
      }
    }

    return collectionData;
  };

  useEffect(() => {
    const tableData = createTableDataPerCollection(aggregation);
    setCollectionData(tableData);
  }, [aggregation]);

  if (!Object.keys(collectionData).length) {
    return null;
  }

  return (
    <div className="w-full flex flex-col gap-5">
      {Object.entries(collectionData).map(([collectionName, fields]) => (
        <div
          key={collectionName}
          className="w-full border-l-4 border-grey-500/40 bg-gradient-to-br from-grey-500/10 via-grey-400/5 to-transparent rounded-xl shadow-lg backdrop-blur-sm hover:border-grey-500/60 transition-all duration-300"
        >
          <div className="p-5 space-y-4">
            <div className="flex flex-col gap-1 sm:flex-row sm:items-baseline sm:justify-between">
              <p className="text-[16px] font-semibold text-primary">
                {collectionName}
              </p>
              <p className="text-[12px] text-secondary">
                {Object.keys(fields).length} mapped fields
              </p>
            </div>

            <div className="flex flex-col gap-4">
              {Object.entries(fields).map(([fieldName, tableData], index) => (
                <div
                  key={`${collectionName}-${fieldName}-${index}`}
                  className="bg-background_alt/80 border border-foreground_alt/25 rounded-lg shadow-sm"
                >
                  <div className="flex items-center justify-between px-4 pt-4 pb-3 border-b border-foreground_alt/20">
                    <div className="flex flex-col">
                      <p className="text-[13px] font-semibold text-primary leading-tight">
                        {fieldName}
                      </p>
                      <span className="text-[11px] text-secondary">
                        {tableData.data.length} rows
                      </span>
                    </div>
                  </div>
                  <div className="px-2.5 pb-4 pt-2">
                    {tableData.data.length > 0 ? (
                      <div className="rounded-lg border border-foreground_alt/20 bg-background p-3 overflow-hidden">
                        <DataTable
                          key={`${collectionName}-${fieldName}`}
                          header={tableData.header}
                          data={tableData.data}
                          stickyHeaders={true}
                          maxHeight="25vh"
                        />
                      </div>
                    ) : (
                      <div className="p-4 text-sm text-secondary">
                        No data available for {fieldName}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default AggregationDisplay;
