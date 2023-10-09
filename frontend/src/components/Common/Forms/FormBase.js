import React from 'react';
import '../../../styles/forms/forms_main.css';
import PropTypes from 'prop-types';

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
          <label className="form-label">
            {field.label}:
            {field.type === 'textarea' ? (
              <textarea {...field.props} className="form-input" />
            ) : field.type === 'select' ? (
              <select {...field.props} className="form-input">
                {field.options &&
                  field.options.map((option) => (
                    <option key={option.label} value={option.value}>
                      {option.label}
                    </option>
                  ))}
              </select>
            ) : (
              <input
                type={field.type}
                {...field.props}
                className="form-input"
              />
            )}
          </label>
        </div>
      ))}
      <button type="submit" className="form-button">
        {buttonText}
      </button>
    </form>
  );
}

FormComponent.propTypes = {
  fields: PropTypes.arrayOf(PropTypes.object).isRequired,
  formClassName: PropTypes.string.isRequired,
  buttonText: PropTypes.string.isRequired,
  onSubmit: PropTypes.func.isRequired,
};
