import React from 'react';
import PropTypes from 'prop-types';
import '../../styles/actions/actions_main.css';
import { logMessage } from '../../api/loging';

const ActionsSection = ({ actionConfigs, executeAction }) => {
  const handleAction = async (Component) => {
    try {
      await executeAction(Component);
      logMessage('info', 'Action executed successfully', 'ActionsSection');
    } catch (error) {
      logMessage(
        'error',
        `Action execution failed: ${error.message}`,
        'ActionsSection',
      );
    }
  };

  const renderElement = (element, elIndex) => {
    switch (element.type) {
      case 'button':
        return (
          <button {...element.props} key={elIndex} className="action-button">
            {element.props.label}
          </button>
        );
      case 'input':
        return (
          <input {...element.props} key={elIndex} className="action-input" />
        );
      case 'status':
        return (
          <div key={elIndex} className="action-status">
            {element.props.status}
          </div>
        );
      case 'file':
        return (
          <div key={elIndex} className="file-wrapper">
            <button
              onClick={() => document.getElementById('file-input').click()}
              className="action-button"
            >
              {element.props.label || 'Select File'}
            </button>
            <input
              type={element.props.type}
              onChange={element.props.onChange}
              id={element.props.id}
              className="file-input"
              style={{ display: 'none' }} // hiding the actual input field
            />
            {element.props.file && (
              <div className="file-name">{element.props.file.name}</div>
            )}
          </div>
        );
      case 'group':
        return (
          <div className="group-wrapper" key={elIndex}>
            {element.children.map((child, childIndex) =>
              renderElement(child, `${elIndex}-${childIndex}`),
            )}
          </div>
        );
      case 'submit':
        return (
          <form {...element.props} key={elIndex} className="action-form">
            {element.children.map((child, childIndex) =>
              renderElement(child, `${elIndex}-${childIndex}`),
            )}
          </form>
        );
      default:
        return null;
    }
  };

  return (
    <div id="actions-section" className="detail-actions">
      {actionConfigs.map(({ type, Component, props }, index) => (
        <div
          key={`action-${index}`}
          id={`action-wrapper-${index}`}
          className="action-wrapper"
        >
          {type === 'button' && (
            <button
              id={`detail-action-button-${index}`}
              className="detail-action"
              onClick={() => handleAction(Component)}
            >
              {Component.label}
            </button>
          )}
          {type === 'link' && (
            <a
              id={`detail-action-link-${index}`}
              className="detail-action"
              href={Component.navigate}
            >
              {Component.label}
            </a>
          )}
          {type === 'element' && (
            <Component {...props}>
              {(elements) =>
                elements.map((element, elIndex) =>
                  renderElement(element, elIndex),
                )
              }
            </Component>
          )}
        </div>
      ))}
    </div>
  );
};

ActionsSection.propTypes = {
  actionConfigs: PropTypes.arrayOf(
    PropTypes.shape({
      type: PropTypes.oneOf(['button', 'element']).isRequired,
      Component: PropTypes.func.isRequired,
      props: PropTypes.object,
    }),
  ).isRequired,
  executeAction: PropTypes.func.isRequired,
};

export default ActionsSection;
