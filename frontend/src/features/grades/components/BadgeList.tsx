'use client';

import React from 'react';
import { Badge } from '../types';

interface BadgeListProps {
  badges: Badge[];
}

export const BadgeList: React.FC<BadgeListProps> = ({ badges }) => {
  return (
    <div className="w-full max-w-5xl mx-auto px-4">
      <div className="flex items-center gap-4 mb-4 pl-2">
        <h2 className="text-xl font-medium text-[#1a4023]">取得したバッチ</h2>
        <div className="relative">
          <select className="text-gray-700 appearance-none bg-white border border-border-[#1a4023] rounded px-4 py-1 pr-8 text-sm focus:outline-none ">
            <option>全て</option>
            <option>座学</option>
            <option>実技</option>
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
            <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
              <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/>
            </svg>
          </div>
        </div>
      </div>
      
      <div className="border-2 border-[#1a4023] rounded-[40px] bg-[#f8fff8] p-8 lg:p-12 min-h-[250px] lg:min-h-[300px] flex items-center justify-around relative overflow-hidden">
        {/* Large Trophy on the left */}
        <div className="flex flex-col items-center justify-center transform scale-125 lg:scale-150">
          <span className="text-[100px] lg:text-[120px] drop-shadow-lg filter">🏆</span>
        </div>

        {/* Medals on the right */}
        <div className="flex gap-8 lg:gap-12 items-end">
          {/* Gold - 1st */}
          <div className="flex flex-col items-center">
             <div className="relative">
               <span className="text-[60px] lg:text-[80px] drop-shadow-md">🥇</span>
               
             </div>
          </div>
          
          {/* Silver - 2nd */}
          <div className="flex flex-col items-center">
             <div className="relative">
               <span className="text-[60px] lg:text-[80px] drop-shadow-md">🥈</span>
               
             </div>
          </div>
          
          {/* Bronze - 3rd */}
          <div className="flex flex-col items-center">
             <div className="relative">
               <span className="text-[60px] lg:text-[80px] drop-shadow-md">🥉</span>
               
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};
