/**
 * ErrorMessage Component
 * スキルツリーのエラー表示
 */

import React from "react";

export interface ErrorMessageProps {
  message: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ message }) => (
  <div className="absolute top-20 left-1/2 -translate-x-1/2 z-30">
    <div className="bg-red-900/90 text-white px-4 py-2 rounded border border-red-700">
      ⚠️ {message}
    </div>
  </div>
);
