import React from 'react';
import { format, subDays, subMonths } from 'date-fns';
import { TimeRange } from '../../types/api';

interface TimeRangeSelectorProps {
  value: TimeRange;
  onChange: (range: TimeRange) => void;
}

const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({ value, onChange }) => {
  const presets = [
    { label: 'Last 7 days', days: 7 },
    { label: 'Last 30 days', days: 30 },
    { label: 'Last 90 days', days: 90 },
  ];

  const handlePresetClick = (days: number) => {
    const end = new Date();
    const start = subDays(end, days);
    onChange({
      start: format(start, 'yyyy-MM-dd'),
      end: format(end, 'yyyy-MM-dd'),
    });
  };

  const handleCustomChange = (type: 'start' | 'end', dateString: string) => {
    onChange({
      ...value,
      [type]: dateString,
    });
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex gap-2">
        {presets.map((preset) => (
          <button
            key={preset.days}
            onClick={() => handlePresetClick(preset.days)}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            {preset.label}
          </button>
        ))}
      </div>
      
      <div className="flex gap-4 items-center">
        <div className="flex flex-col gap-1">
          <label htmlFor="start-date" className="text-sm font-medium text-gray-700">
            Start Date
          </label>
          <input
            id="start-date"
            type="date"
            value={value.start}
            onChange={(e) => handleCustomChange('start', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        
        <div className="flex flex-col gap-1">
          <label htmlFor="end-date" className="text-sm font-medium text-gray-700">
            End Date
          </label>
          <input
            id="end-date"
            type="date"
            value={value.end}
            onChange={(e) => handleCustomChange('end', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>
  );
};

export default TimeRangeSelector;
