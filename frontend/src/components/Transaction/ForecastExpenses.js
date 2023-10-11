import React, { useEffect, useState } from 'react';
import { forecastExpenses } from '../../api/transaction';

const ForecastExpenses = () => {
  const [loading, setLoading] = useState(false); // set initial loading state to false
  const [forecast, setForecast] = useState(null);
  const [startForecast, setStartForecast] = useState(false); // new state to track button click

  useEffect(() => {
    const fetchForecast = async () => {
      let response = await forecastExpenses(); // get the task id

      while (response.status === 'Pending') {
        // delay of 1 second before checking again
        await new Promise((resolve) => setTimeout(resolve, 1000));
        response = await forecastExpenses(); // check the task status again
      }

      if (response.status === 'Complete') {
        setForecast(response.result); // set the result in state
        setLoading(false); // stop loading
      }
    };

    if (startForecast) {
      // only start the forecast when the button is clicked
      setLoading(true);
      fetchForecast(); // call the function
    }
  }, [startForecast]); // depend on startForecast state so it reruns when the button is clicked

  return (
    <div>
      <button onClick={() => setStartForecast(true)}>Start Forecast</button>
      {
        loading ? (
          <div>Loading...</div> // render some loading state
        ) : (
          <div>Forecasted expenses: {forecast}</div>
        ) // render the forecast or nothing if it hasn't started
      }
    </div>
  );
};

export default ForecastExpenses;
