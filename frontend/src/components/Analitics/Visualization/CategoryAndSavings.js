import React from 'react';
import PropTypes from 'prop-types';
import { Pie } from 'react-chartjs-2';
import { Chart, ArcElement, CategoryScale, Title, Tooltip } from 'chart.js';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';

// Register chart elements
Chart.register(ArcElement, CategoryScale, Title, Tooltip);

const CategoryAndSavings = ({
  category,
  selected_category_spending,
  potential_savings,
}) => {
  // Data for Pie chart
  const pieData = {
    labels: ['Spent', 'Potential Savings'],
    datasets: [
      {
        data: [selected_category_spending, potential_savings],
        backgroundColor: ['#FFA07A', '#20B2AA'],
      },
    ],
  };

  // Calculate percentage of potential savings
  const savingPercentage = (
    (potential_savings / selected_category_spending) *
    100
  ).toFixed(2);

  return (
    <div className="category-and-savings">
      <h2>{category}</h2>
      <div className="chart-wrapper">
        <Pie data={pieData} />
        <div style={{ width: '100px', height: '100px', margin: '0 20px' }}>
          <CircularProgressbar
            value={savingPercentage}
            text={`${savingPercentage}%`}
            styles={buildStyles({
              // Customized styles
              pathColor: `rgba(62, 152, 199, ${savingPercentage / 100})`,
              textColor: '#f88',
              trailColor: '#d6d6d6',
              backgroundColor: '#3e98c7',
            })}
          />
        </div>
      </div>
    </div>
  );
};

CategoryAndSavings.propTypes = {
  category: PropTypes.string.isRequired,
  selected_category_spending: PropTypes.number.isRequired,
  potential_savings: PropTypes.number.isRequired,
};

export default CategoryAndSavings;
