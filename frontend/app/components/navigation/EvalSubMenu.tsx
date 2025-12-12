"use client";

import React, { useContext, useState } from "react";
import { useEffect } from "react";

import {
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarGroupLabel,
} from "@/components/ui/sidebar";

import { MdOutlineSpaceDashboard } from "react-icons/md";
import { MdOutlineFeedback } from "react-icons/md";

import { EvaluationContext } from "../contexts/EvaluationContext";

import { RouterContext } from "../contexts/RouterContext";
import { useSearchParams } from "next/navigation";

const EvalSubMenu: React.FC = () => {
  const searchParams = useSearchParams();

  const [currentDisplay, setCurrentDisplay] = useState<string | null>(null);

  const { changeEvalPage } = useContext(EvaluationContext);

  const { changePage, currentPage } = useContext(RouterContext);

  const toDashboard = () => {
    changePage("eval", {}, true);
  };

  const toDisplay = (display: string) => {
    changeEvalPage(null);
    changePage("display", { type: display }, true);
  };

  // Display components ordered for narrative flow: simple → complex
  // Follows the analytical workflow an intelligence analyst would use
  // See examples/README.md "UI Preview" section for documentation
  const displays = [
    // Stage 1: Orientation
    { name: "Initial Response", path: "initial_response" },
    { name: "Text Response", path: "text_response" },
    { name: "Single Message", path: "singleMessage" },
    // Stage 2: Evidence Examination
    { name: "Document", path: "document" },
    { name: "Table", path: "table" },
    { name: "Aggregation", path: "aggregation" },
    // Stage 3: Visualization
    { name: "Chart", path: "chart" },
    { name: "Bar Chart", path: "bar_chart" },
    { name: "Thread", path: "thread" },
    { name: "Network Chart", path: "network_chart" },
    { name: "Mapbox", path: "mapbox" },
    // Stage 4: Synthesis
    { name: "Intelligence Agent", path: "intelligence_agent" },
    { name: "Courthouse Debate", path: "courthouse_debate" },

     { name: "Tickets", path: "tickets" },
    { name: "Products", path: "product" },
  ];

  useEffect(() => {
    const displayParam = searchParams.get("type");
    if (displayParam) {
      setCurrentDisplay(displayParam);
    }
  }, [searchParams]);

  return (
    <>
      <SidebarGroup>
        <SidebarGroupLabel>
          <p>Evaluation</p>
        </SidebarGroupLabel>
        <SidebarMenuItem className="list-none" key={"dashboard"}>
          <SidebarMenuButton
            variant={currentPage === "eval" ? "active" : "default"}
            onClick={toDashboard}
          >
            <MdOutlineSpaceDashboard />
            <p>Dashboard</p>
          </SidebarMenuButton>
        </SidebarMenuItem>
        <SidebarMenuItem className="list-none" key={"Feedback Button"}>
          <SidebarMenuButton
            variant={currentPage === "feedback" ? "active" : "default"}
            onClick={() => changePage("feedback", {}, true)}
          >
            <MdOutlineFeedback />
            <p>Feedback</p>
          </SidebarMenuButton>
        </SidebarMenuItem>
      </SidebarGroup>
      {process.env.NODE_ENV === "development" && (
        <SidebarGroup>
          <SidebarGroupLabel>
            <p>Displays</p>
          </SidebarGroupLabel>
          <SidebarGroupContent>
            {displays.map((display) => (
              <SidebarMenuItem className="list-none" key={display.path}>
                <SidebarMenuButton
                  variant={
                    currentDisplay === display.path ? "active" : "default"
                  }
                  className="text-secondary text-sm"
                  onClick={() => toDisplay(display.path)}
                >
                  {display.name}
                </SidebarMenuButton>
              </SidebarMenuItem>
            ))}
          </SidebarGroupContent>
        </SidebarGroup>
      )}
    </>
  );
};

export default EvalSubMenu;
