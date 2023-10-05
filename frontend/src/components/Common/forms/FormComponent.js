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
