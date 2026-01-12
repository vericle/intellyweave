"use client";

import DataTable from "@/app/components/explorer/DataTable";

interface BoringGenericDisplayProps {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  payload: { [key: string]: any }[];
}

const BoringGenericDisplay: React.FC<BoringGenericDisplayProps> = ({
  payload,
}) => {
  if (!payload || payload.length === 0) {
    return null;
  }

  const shouldDisplayColumn = (columnKey: string): boolean => {
    if (!columnKey) return false;
    if (columnKey.startsWith("_")) return false;
    if (columnKey === columnKey.toUpperCase()) return false;
    return true;
  };

  const deriveColumnType = (value: unknown): string => {
    if (value === null || value === undefined) return "text";
    if (Array.isArray(value)) return "text[]";
    if (typeof value === "number") return "number";
    if (typeof value === "boolean") return "boolean";
    if (typeof value === "object") return "object";
    return "text";
  };

  const filteredData = payload.map((row) => {
    const cleanedRow: { [key: string]: unknown } = {};
    Object.entries(row).forEach(([key, value]) => {
      if (shouldDisplayColumn(key)) {
        cleanedRow[key] = value;
      }
    });
    return cleanedRow;
  });

  const filteredHeader = filteredData.length
    ? Object.keys(filteredData[0]).reduce<{ [key: string]: string }>((acc, key) => {
        acc[key] = deriveColumnType(filteredData[0][key]);
        return acc;
      }, {})
    : {};

  return (
    <div className="w-full border-l-4 border-grey-500/40 bg-gradient-to-br from-grey-500/10 via-grey-400/5 to-transparent rounded-xl shadow-lg backdrop-blur-sm hover:border-grey-500/60 transition-all duration-300">
      <div className="w-full p-5 space-y-3">
        <div className="flex flex-col gap-1 sm:flex-row sm:items-center sm:justify-between">
          <p className="text-base font-semibold text-primary">Table View</p>
          <p className="text-xs text-primary/60">
            {filteredData.length} rows · {Object.keys(filteredHeader).length} columns
          </p>
        </div>
        <div className="rounded-lg border border-foreground_alt/25 bg-background_alt/80 p-3 overflow-hidden">
          <DataTable
            data={filteredData as { [key: string]: unknown }[]}
            header={filteredHeader}
            stickyHeaders={true}
            maxHeight="30vh"
          />
        </div>
      </div>
    </div>
  );
};

export default BoringGenericDisplay;
