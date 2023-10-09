import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import PropTypes from 'prop-types';
import ActionsSection from '../../Common/Actions';
import '../../../styles/detail/detail_main.css';

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
      .then((data) => setEntity(data))
      .catch((error) => console.error(error));
  }, [id, fetchDetail]);

  const executeAction = (action) => {
    action
      .execute(id)
      .then(() => {
        if (action.navigate) {
          navigate(action.navigate);
        }
      })
      .catch((error) => console.error(error));
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
