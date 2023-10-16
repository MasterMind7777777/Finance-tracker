import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import ActionsSection from '../../Common/Actions';
import '../../../styles/detail/detail_main.css';
import { logMessage } from '../../../api/loging';

export const DetailComponent = ({
  fetchDetail,
  detailFields,
  actionConfigs,
  entityTitle,
}) => {
  const { id } = useParams();
  const [entity, setEntity] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDetail(id)
      .then((data) => {
        setEntity(data);
        logMessage(
          'info',
          `Successfully fetched details for entity ID: ${id}`,
          'DetailComponent',
        ); // Log success
      })
      .catch((error) => {
        logMessage(
          'error',
          `Error fetching entity ID: ${id}. Error: ${error.message}`,
          'DetailComponent',
        ); // Log error
        console.error(error);
      });
  }, [id, fetchDetail]);

  const executeAction = (action) => {
    action
      .execute(id)
      .then(() => {
        logMessage(
          'info',
          `Successfully executed action for entity ID: ${id}`,
          'DetailComponent',
        ); // Log action success
        if (action.navigate) {
          navigate(action.navigate);
        }
      })
      .catch((error) => {
        logMessage(
          'error',
          `Failed to execute action for entity ID: ${id}. Error: ${error.message}`,
          'DetailComponent',
        ); // Log action failure
        console.error(error);
      });
  };

  if (!entity) {
    return <div id="loading-wrapper">Loading...</div>;
  }

  return (
    <div id="detail-card-wrapper" className="detail-card">
      {/* Title Section */}
      <div className="title-section">
        <h1 className="detail-title">{entityTitle}</h1>
      </div>

      {/* Content Section */}
      <div id="content-section" className="detail-content">
        {detailFields.map((field, index) => (
          <div
            key={`field-${index}`}
            id={`detail-field-wrapper-${index}`} // Dynamic ID
            className="detail-field detail-field-wrapper" // Static and dynamic class names
          >
            <strong id={`detail-label-${index}`} className="detail-label">
              {field.label}:
            </strong>
            <span id={`detail-value-${index}`} className="detail-value">
              {entity[field.key]}
            </span>
          </div>
        ))}
      </div>

      {/* Actions Section */}
      {actionConfigs && actionConfigs.length > 0 && (
        <ActionsSection
          actionConfigs={actionConfigs}
          executeAction={executeAction}
        />
      )}
    </div>
  );
};

DetailComponent.propTypes = {
  entityTitle: PropTypes.string.isRequired,
  fetchDetail: PropTypes.func.isRequired,
  detailFields: PropTypes.arrayOf(
    PropTypes.shape({
      key: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
    }),
  ).isRequired,
  actionConfigs: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.oneOf(['button', 'form']).isRequired,
      Component: PropTypes.func.isRequired,
      props: PropTypes.object,
    }),
  ),
};

DetailComponent.defaultProps = {
  actionConfigs: null,
};
