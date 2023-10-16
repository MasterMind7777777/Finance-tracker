import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { useParams } from 'react-router-dom';
import { getSavingsOpportunities } from '../../api/transaction';
import CategoryAndSavings from './Visualization/CategoryAndSavings';
import AssociationRuleChart from './Visualization/AssociationRuleChart';
import '../../styles/visualisaton/SavingsOpportunities.css';
import { logMessage } from '../../api/loging';

const AssociationRule = ({ rule }) => (
  <li>
    <div>Antecedents: {rule.antecedents.join(', ')}</div>
    <div>Consequents: {rule.consequents.join(', ')}</div>
    <div>Support: {rule.support}</div>
    <div>Confidence: {rule.confidence}</div>
  </li>
);

AssociationRule.propTypes = {
  rule: PropTypes.shape({
    antecedents: PropTypes.arrayOf(PropTypes.string).isRequired,
    consequents: PropTypes.arrayOf(PropTypes.string).isRequired,
    support: PropTypes.number.isRequired,
    confidence: PropTypes.number.isRequired,
  }).isRequired,
};

const CategoryItem = ({ item }) => (
  <div className="category-item">
    <div className="category-info">
      <p className="category-spending">
        Total Category Spending: {item.selected_category_spending}
      </p>
      <p className="category-savings">
        Potential Savings: {item.potential_savings}
      </p>
    </div>
    <CategoryAndSavings
      className="category-and-savings"
      category={item.category}
      selected_category_spending={item.selected_category_spending}
      potential_savings={item.potential_savings}
    />

    <div className="association-rules">
      <h3 className="association-title">Association Rules:</h3>
      {item.association_rules?.length > 0 ? (
        <>
          <ul className="rule-list">
            {item.association_rules.map((rule) => (
              <AssociationRule
                className="rule-item"
                key={rule.antecedents.join('_')}
                rule={rule}
              />
            ))}
          </ul>
          <AssociationRuleChart
            className="association-chart"
            association_rules={item.association_rules}
          />
        </>
      ) : (
        <p className="no-rules">No association rules available.</p>
      )}
    </div>
  </div>
);

CategoryItem.propTypes = {
  item: PropTypes.shape({
    category: PropTypes.string.isRequired,
    potential_savings: PropTypes.number.isRequired,
    selected_category_spending: PropTypes.number.isRequired,
    association_rules: PropTypes.arrayOf(
      PropTypes.shape({
        antecedents: PropTypes.arrayOf(PropTypes.string),
        consequents: PropTypes.arrayOf(PropTypes.string),
        support: PropTypes.number,
        confidence: PropTypes.number,
      }),
    ),
  }).isRequired,
};

const SavingsOpportunities = () => {
  const { id: categoryId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        logMessage(
          'info',
          `Fetching savings opportunities for category ID: ${categoryId}`,
          'SavingsOpportunities',
        );
        const result = await getSavingsOpportunities(categoryId);
        setData(result);
        logMessage(
          'info',
          `Data fetched successfully for category ID: ${categoryId}`,
          'SavingsOpportunities',
        );
      } catch (error) {
        logMessage(
          'error',
          `Error fetching data for category ID: ${categoryId}. Error: ${error}`,
          'SavingsOpportunities',
        );
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [categoryId]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="savings-opportunities">
      <h1 className="main-title">Savings Opportunities</h1>
      <div className="category-list">
        {data ? (
          data.map((item, index) => (
            <CategoryItem
              className="category-list-item"
              key={index}
              item={item}
            />
          ))
        ) : (
          <p className="error-message">An error occurred.</p>
        )}
      </div>
    </div>
  );
};

export default SavingsOpportunities;
