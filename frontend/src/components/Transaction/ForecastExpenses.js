import React, { useEffect, useState } from 'react';
import { forecastExpenses } from '../../api/transaction';
import { logMessage } from '../../api/loging'; // Import logMessage function

const ForecastExpenses = () => {
  const [loading, setLoading] = useState(false);
  const [forecast, setForecast] = useState(null);
  const [startForecast, setStartForecast] = useState(false);

  useEffect(() => {
    const fetchForecast = async () => {
      try {
        let response = await forecastExpenses(); // get the task id
        logMessage('info', 'Forecast process initiated', 'ForecastExpenses');

        while (response.status === 'Pending') {
          await new Promise((resolve) => setTimeout(resolve, 1000));
          response = await forecastExpenses(); // check the task status again
        }

        if (response.status === 'Complete') {
          setForecast(response.result); // set the result in state
          setLoading(false); // stop loading
          logMessage('info', 'Forecast process completed', 'ForecastExpenses');
        }
      } catch (error) {
        setLoading(false); // stop loading
        logMessage(
          'error',
          `Error in forecast process: ${error.message}`,
          'ForecastExpenses',
        );
      }
    };

    if (startForecast) {
      setLoading(true);
      fetchForecast(); // call the function
    }
  }, [startForecast]);

  return (
    <div>
      <button onClick={() => setStartForecast(true)}>Start Forecast</button>
      {loading ? (
        <div>Loading...</div>
      ) : (
        <div>Forecasted expenses: {forecast}</div>
      )}
    </div>
  );
};

export default ForecastExpenses;
