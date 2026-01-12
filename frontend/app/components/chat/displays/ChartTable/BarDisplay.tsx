"use client";

import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import { ResultPayload } from "@/app/types/chat";
import { BarPayload } from "@/app/types/displays";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { getChartColorByIndex } from "@/app/utils/colorMap";

/**
 * Tooltip aligned to design system
 */
const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;

  return (
    <div className="bg-background/95 border border-foreground_alt/40 rounded-lg px-3 py-2 shadow-xl">
      <p className="text-[13px] text-primary font-medium mb-1">{label}</p>

      {payload.map((entry: any, index: number) => (
        <p
          key={index}
          className="text-[12px] leading-tight"
          style={{ color: entry.color }}
        >
          {entry.dataKey}: {entry.value}
        </p>
      ))}
    </div>
  );
};

interface BarDisplayProps {
  result: ResultPayload;
}

const BarDisplay: React.FC<BarDisplayProps> = ({ result }) => {
  const transformChartData = (chartItem: BarPayload) => {
    const { x_labels, y_values } = chartItem.data;
    const data: any[] = [];

    x_labels.forEach((label, i) => {
      const row: any = { x: label };
      for (const key of Object.keys(y_values)) {
        row[key] = y_values[key][i] ?? null;
      }
      data.push(row);
    });

    return { data, yKeys: Object.keys(y_values) };
  };

  return (
    <div className="w-full space-y-8">
      {(result.objects as BarPayload[]).map((chartItem, index) => {
        const { data, yKeys } = transformChartData(chartItem);

        return (
          <Card
            key={chartItem._REF_ID || index}
            className="
              w-full
              border-l-4 border-grey-500/40
              bg-gradient-to-br from-grey-500/10 via-grey-400/5 to-transparent
              hover:border-grey-500/60
              transition-all duration-300 ease-in-out
              backdrop-blur-sm
              shadow-lg
              rounded-xl
            "
          >
            {/* Header */}
            <div className="p-5 space-y-3">
              <div className="flex flex-col gap-1">
                <h2 className="text-[16px] font-semibold text-primary">
                  {chartItem.title}
                </h2>
                <p className="text-[13px] text-secondary leading-relaxed">
                  {chartItem.description}
                </p>

                <div className="flex items-center gap-2 flex-wrap mt-1">
                  <Badge
                    variant="outline"
                    className="border-foreground_alt/30 text-[10px] text-secondary"
                  >
                    Data points: {data.length}
                  </Badge>
                  <Badge
                    variant="outline"
                    className="border-foreground_alt/30 text-[10px] text-secondary"
                  >
                    Series: {yKeys.length}
                  </Badge>
                </div>
              </div>

              <Separator className="bg-foreground_alt/20" />

              <div className="w-full h-[320px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={data}
                    margin={{ top: 8, right: 12, left: 4, bottom: 8 }}
                  >
                    {/* GRID */}
                    <CartesianGrid
                      stroke="hsl(var(--foreground_alt) / 0.2)"
                      vertical={false}
                      strokeDasharray="3 3"
                    />

                    {/* AXES */}
                    <XAxis
                      dataKey="x"
                      tick={{ fill: "hsl(var(--secondary))", fontSize: 12 }}
                      axisLine={{ stroke: "hsl(var(--foreground_alt))" }}
                      tickLine={false}
                    />

                    <YAxis
                      tick={{ fill: "hsl(var(--secondary))", fontSize: 12 }}
                      axisLine={{ stroke: "hsl(var(--foreground_alt))" }}
                      tickLine={false}
                    />

                    <Tooltip content={<CustomTooltip />} />

                    <Legend
                      wrapperStyle={{
                        fontSize: "12px",
                        paddingTop: "6px",
                        color: "hsl(var(--secondary))",
                      }}
                    />

                    {/* GRADIENT DEFINITIONS */}
                    <defs>
                      {yKeys.map((_, idx) => {
                        const baseColor = getChartColorByIndex(idx);
                        return (
                          <linearGradient
                            key={idx}
                            id={`bar-gradient-${idx}`}
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                          >
                            {/* Highlight top */}
                            <stop
                              offset="0%"
                              stopColor={baseColor}
                              stopOpacity="0.95"
                            />
                            {/* Saturated mid */}
                            <stop
                              offset="50%"
                              stopColor={baseColor}
                              stopOpacity="0.80"
                            />
                            {/* Faded bottom */}
                            <stop
                              offset="100%"
                              stopColor={baseColor}
                              stopOpacity="0.40"
                            />
                          </linearGradient>
                        );
                      })}
                    </defs>

                    {/* BARS */}
                    {yKeys.map((key, idx) => (
                      <Bar
                        key={key}
                        dataKey={key}
                        radius={[4, 4, 0, 0]}
                        fill={`url(#bar-gradient-${idx})`}
                      />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
};

export default BarDisplay;