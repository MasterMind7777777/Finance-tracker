import React, { memo, useEffect, useRef } from 'react';
import PropTypes from 'prop-types';
import { Radar } from 'react-chartjs-2';
import { Chart, RadialLinearScale, PointElement, LineElement } from 'chart.js';
import '../../../styles/visualisaton/AssociationRuleChart.css';

// Register the scale and elements
Chart.register(RadialLinearScale, PointElement, LineElement);

const prepareRadarData = (rule) => ({
  labels: [
    'Support',
    'Confidence',
    'Lift',
    'Leverage',
    'Conviction',
    'Zhangs Metric',
  ],
  datasets: [
    {
      data: [
        rule.support,
        rule.confidence,
        rule.lift,
        rule.leverage,
        isNaN(parseFloat(rule.conviction)) ? 0 : parseFloat(rule.conviction),
        rule.zhangs_metric,
      ],
      backgroundColor: 'rgba(54, 162, 235, 0.2)',
      borderColor: 'rgba(54, 162, 235, 1)',
    },
  ],
});

const AssociationRuleChart = ({ association_rules }) => {
  const chartRefs = useRef([]);

  useEffect(() => {
    chartRefs.current.forEach((ref) => {
      if (ref) {
        ref.destroy();
      }
    });
    chartRefs.current = [];

    return () => {
      chartRefs.current.forEach((ref) => ref && ref.destroy());
    };
  }, [association_rules]);

  return (
    <div>
      <h2>Association Rules</h2>
      {association_rules.map((rule, index) => (
        <div key={index}>
          <h3>
            Rule {index + 1}: {rule.antecedents.join(', ')} {'=>'}{' '}
            {rule.consequents.join(', ')}
          </h3>
          <Radar
            ref={(ref) => (chartRefs.current[index] = ref?.chartInstance)}
            data={prepareRadarData(rule)}
          />
        </div>
      ))}
    </div>
  );
};

AssociationRuleChart.propTypes = {
  association_rules: PropTypes.arrayOf(
    PropTypes.shape({
      antecedents: PropTypes.arrayOf(PropTypes.string).isRequired,
      consequents: PropTypes.arrayOf(PropTypes.string).isRequired,
      support: PropTypes.number.isRequired,
      confidence: PropTypes.number.isRequired,
      lift: PropTypes.number.isRequired,
      leverage: PropTypes.number.isRequired,
      conviction: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
        .isRequired,
      zhangs_metric: PropTypes.number.isRequired,
    }),
  ).isRequired,
};

const MemoizedAssociationRuleChart = memo(AssociationRuleChart);

export default MemoizedAssociationRuleChart;
