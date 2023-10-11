import React, { useState, useEffect } from 'react';
import { getTransactionRecommendations } from '../../api/transaction';

const RecommendationComponent = ({ numRecommendations }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [mostUsedCategory, setMostUsedCategory] = useState(null); // FIXME name insed of id

  useEffect(() => {
    getTransactionRecommendations(numRecommendations)
      .then((response) => {
        if (response) {
          setRecommendations(response.recommendations);
          setMostUsedCategory(response.most_used_category);
        }
      })
      .catch((error) => {
        console.error('Failed to fetch transaction recommendations:', error);
      });
  }, [numRecommendations]);

  return (
    <div>
      <h2>
        Your transaction recommendations based on the most used category:{' '}
        {mostUsedCategory}
      </h2>
      <ul>
        {recommendations.map((recommendation, index) => (
          <li key={index}>
            <h3>{recommendation.title}</h3>
            <p>{recommendation.description}</p>
            <p>Amount: {recommendation.amount}</p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default RecommendationComponent;
