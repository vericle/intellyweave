"use client";

import React, { useContext, useState } from "react";
import { motion } from "framer-motion";
import { PiGlobe } from "react-icons/pi";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

import { HiMiniSparkles } from "react-icons/hi2";
import { Checkbox } from "@/components/ui/checkbox";
import { useEffect } from "react";

import { Button } from "@/components/ui/button";
import { SessionContext } from "@/app/components/contexts/SessionContext";
import { RouterContext } from "../contexts/RouterContext";
import { CollectionContext } from "../contexts/CollectionContext";

const StartDialog: React.FC = () => {
  const { changePage } = useContext(RouterContext);
  const dontShowAgainKey = "INTELLYWEAVE_START_DIALOG_DONT_SHOW_AGAIN";
  const { correctSettings } = useContext(SessionContext);
  const { collections } = useContext(CollectionContext);
  const [open, setOpen] = useState(() => {
    // Check if we're in the browser environment
    if (typeof window !== "undefined") {
      const dontShow = localStorage.getItem(dontShowAgainKey);
      return dontShow ? false : true;
    }
    return true; // Default to showing dialog on server-side render
  });
  const [dontShowAgain, setDontShowAgain] = useState(false);
  const [invalidSettings, setInvalidSettings] = useState(false);

  useEffect(() => {
    if (correctSettings) {
      const hasIncorrectSettings = Object.values(correctSettings).some(
        (setting) => !setting
      );
      if (!hasIncorrectSettings) {
        setInvalidSettings(false);
      } else {
        if (collections.length === 0) {
          setInvalidSettings(true);
        }
      }
    }
  }, [correctSettings, collections.length]);

  const handleCheck = () => {
    setDontShowAgain((prev) => !prev);
  };

  const handleClose = () => {
    if (dontShowAgain) {
      localStorage.setItem(dontShowAgainKey, "true");
    }
    setOpen(false);
  };

  const handleGetStarted = () => {
    if (invalidSettings) {
      changePage("settings");
    }
    if (dontShowAgain) {
      localStorage.setItem(dontShowAgainKey, "true");
    }
    setOpen(false);
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="w-full max-w-[95vw] sm:max-w-2xl max-h-[90vh] sm:max-h-[80vh] overflow-y-auto">
        <div className="max-h-full overflow-y-auto space-y-4">
          <DialogHeader>
            <DialogTitle className="flex gap-3 items-center justify-start">
              <p className="text-primary text-3xl font-bold">
                Welcome to IntellyWeave!
              </p>
            </DialogTitle>
            <DialogDescription className="flex justify-start">
              Your AI Intelligence Assistant
            </DialogDescription>
          </DialogHeader>
          <div className="flex flex-col gap-4">
            <div className="flex flex-col items-center gap-4">
              <div className="w-full space-y-3">
                <p className="font-semibold text-primary">Quick Start Guide:</p>
                <div className="space-y-2 text-sm">
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">1.</span>
                    <span>Head to <strong>Settings</strong> to configure your AI models and Weaviate cluster</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">2.</span>
                    <span>Go to <strong>Agents & Documents</strong> to create intelligence agents and upload documents</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">3.</span>
                    <span>Use the <strong>Chat</strong> interface to interact with your AI intelligence assistant</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="text-primary font-bold">4.</span>
                    <span>View the <strong>Data</strong> section to manage your intelligence document collections</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <DialogFooter>
            <div className="flex flex-col justify-between w-full gap-4">
              <div className="flex w-full justify-start gap-2 items-center">
                <Checkbox
                  id="dontshowagain"
                  checked={dontShowAgain}
                  onCheckedChange={handleCheck}
                />
                <p className="text-sm text-secondary">Don&apos;t show again</p>
              </div>
              <div className="flex flex-col items-center w-full gap-3">
                <p className="text-center text-sm text-muted-foreground inline-flex">
                  Enjoy the journey ... <PiGlobe />
                </p>
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  whileTap={{ scale: 0.98 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="w-full max-w-md"
                >
                  <Button
                    className="w-full bg-gradient-to-r from-green-800 via-green-700 to-green-500 hover:from-green-900 hover:via-green-800 hover:to-green-700 text-white"
                    size="default"
                    onClick={handleGetStarted}
                  >
                    <HiMiniSparkles />
                    {invalidSettings ? "Get Started - Configure Settings" : "Let's Go!"}
                  </Button>
                </motion.div>
              </div>
            </div>
          </DialogFooter>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default StartDialog;
