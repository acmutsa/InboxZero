'use client';

import { useEffect, useRef, useState } from 'react';
import {
  Bar,
  BarChart,
  LabelList,
  Pie,
  PieChart,
  XAxis,
  YAxis,
} from 'recharts';
import { Card } from '@/components/ui/card';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from '@/components/ui/chart';
import {
  emailCategories,
  gmailTotal,
  outlookTotal,
  emailTotal,
  draftCounts,
  draftTotal,
  draftPercentage,
  draftRequirements,
} from '@/lib/demo-analytics';

const categoryConfig = {
  gmail: { label: 'Gmail', color: 'var(--primary)' },
  outlook: { label: 'Outlook', color: 'var(--muted-foreground)' },
} satisfies ChartConfig;
const draftConfig = {
  required: { label: 'Draft required', color: 'var(--primary)' },
  notRequired: { label: 'No draft', color: 'var(--border)' },
} satisfies ChartConfig;

function useChartEntrance() {
  const ref = useRef<HTMLDivElement>(null);
  const [entrance, setEntrance] = useState<'waiting' | 'animate' | 'static'>(
    'waiting',
  );

  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries.some((entry) => entry.isIntersecting)) {
          setEntrance(motion.matches ? 'static' : 'animate');
          observer.disconnect();
        }
      },
      { threshold: 0.25 },
    );
    const onMotionChange = () => {
      if (motion.matches)
        setEntrance((previous) =>
          previous === 'waiting' ? previous : 'static',
        );
    };
    motion.addEventListener('change', onMotionChange);
    observer.observe(element);
    return () => {
      observer.disconnect();
      motion.removeEventListener('change', onMotionChange);
    };
  }, []);

  return {
    ref,
    ready: entrance !== 'waiting',
    animate: entrance === 'animate',
  };
}

export function CategoryChart() {
  const { ref, ready, animate } = useChartEntrance();
  return (
    <Card ref={ref} className="chart-card">
      <h3>Emails by category</h3>
      <div className="chart-legend">
        <span>
          <i className="legend-gmail" />
          Gmail
        </span>
        <span>
          <i className="legend-outlook" />
          Outlook
        </span>
        <small>Scale: 0–150 emails</small>
      </div>
      {ready ? (
        <ChartContainer
          config={categoryConfig}
          className="category-chart"
          aria-label="Email counts by category and provider"
        >
          <BarChart
            accessibilityLayer
            data={emailCategories}
            margin={{ top: 24, right: 4, bottom: 12, left: -22 }}
            barGap={6}
          >
            <XAxis
              dataKey="category"
              axisLine={false}
              tickLine={false}
              tickMargin={12}
              interval={0}
              tick={{
                fontSize: 11,
                fill: 'var(--foreground)',
                fontWeight: 500,
              }}
              tickFormatter={(value) =>
                value === 'Notification'
                  ? 'Notify'
                  : value === 'Newsletter'
                    ? 'News'
                    : value === 'Scheduling'
                      ? 'Schedule'
                      : value
              }
            />
            <YAxis
              domain={[0, 150]}
              ticks={[0, 50, 100, 150]}
              axisLine={false}
              tickLine={false}
              tick={{
                fontSize: 12,
                fill: 'var(--foreground)',
                fontWeight: 500,
              }}
            />
            <ChartTooltip cursor={false} content={<ChartTooltipContent />} />
            <Bar
              dataKey="gmail"
              fill="var(--color-gmail)"
              radius={8}
              maxBarSize={27}
              isAnimationActive={animate}
              animationDuration={900}
              animationEasing="ease-out"
            >
              <LabelList
                dataKey="gmail"
                position="top"
                fontSize={10}
                fill="var(--muted-foreground)"
              />
            </Bar>
            <Bar
              dataKey="outlook"
              fill="var(--color-outlook)"
              radius={8}
              maxBarSize={27}
              isAnimationActive={animate}
              animationDuration={900}
              animationEasing="ease-out"
            >
              <LabelList
                dataKey="outlook"
                position="top"
                fontSize={10}
                fill="var(--muted-foreground)"
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      ) : (
        <div style={{ height: 300 }} aria-hidden="true" />
      )}
      <table className="sr-only">
        <caption>Email counts by category, last 30 days — sample data</caption>
        <thead>
          <tr>
            <th scope="col">Category</th>
            <th scope="col">Gmail</th>
            <th scope="col">Outlook</th>
          </tr>
        </thead>
        <tbody>
          {emailCategories.map((row) => (
            <tr key={row.category}>
              <th scope="row">{row.category}</th>
              <td>{row.gmail}</td>
              <td>{row.outlook}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

export function DraftChart() {
  const { ref, ready, animate } = useChartEntrance();
  return (
    <Card ref={ref} className="draft-analysis">
      <h3>Draft requirements</h3>
      <div className="donut">
        {ready && (
          <ChartContainer
            config={draftConfig}
            className="draft-chart"
            aria-label={`${draftTotal} emails require a draft; ${emailTotal - draftTotal} do not.`}
          >
            <PieChart accessibilityLayer>
              <ChartTooltip
                content={<ChartTooltipContent nameKey="name" hideLabel />}
              />
              <Pie
                data={draftRequirements}
                dataKey="count"
                nameKey="name"
                innerRadius={69}
                outerRadius={90}
                startAngle={90}
                endAngle={-270}
                stroke="none"
                isAnimationActive={animate}
                animationDuration={1100}
                animationEasing="ease-out"
              />
            </PieChart>
          </ChartContainer>
        )}
        <div className="donut-total">
          <strong>{emailTotal}</strong>
          <small>TOTAL EMAILS</small>
        </div>
      </div>
      <h4>{draftPercentage}% needed a draft</h4>
      <p>
        ■ Draft required&nbsp; {draftTotal} &nbsp; □ No draft&nbsp;{' '}
        {emailTotal - draftTotal}
      </p>
      <p>
        Gmail: {draftCounts.gmail} draft / {gmailTotal - draftCounts.gmail} no
        draft
      </p>
      <p>
        Outlook: {draftCounts.outlook} draft /{' '}
        {outlookTotal - draftCounts.outlook} no draft
      </p>
    </Card>
  );
}
