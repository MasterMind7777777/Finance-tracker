import React from 'react'; // Add this if you're using React version < 17 or haven't updated your ESLint config
import '../../../styles/forms/forms_main.css';
import PropTypes from 'prop-types'; // If you intend to use PropTypes

export default function FormComponent({
  fields,
  formClassName,
  buttonText,
  onSubmit,
}) {
  return (
    <form className={`form ${formClassName}`} onSubmit={onSubmit}>
      {fields.map((field, index) => (
        <div className="form-group" key={index}>
          {field.label && (
            <label className="form-label">
              {field.label}:
              {field.type === 'textarea' ? (
                <textarea {...field.props} className="form-input" />
              ) : (
                <input
                  type={field.type}
                  {...field.props}
                  className="form-input"
                />
              )}
            </label>
          )}
          {!field.label &&
            (field.type === 'textarea' ? (
              <textarea {...field.props} className="form-input" />
            ) : (
              <input
                type={field.type}
                {...field.props}
                className="form-input"
              />
            ))}
        </div>
      ))}
      <button type="submit" className="form-button">
        {buttonText}
      </button>
    </form>
  );
}

// If you're using PropTypes, add this:
FormComponent.propTypes = {
  fields: PropTypes.arrayOf(PropTypes.object).isRequired,
  formClassName: PropTypes.string.isRequired,
  buttonText: PropTypes.string.isRequired,
  onSubmit: PropTypes.func.isRequired,
};
