import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import '../../../styles/lists/lists_main.css';

const defaultRenderContent = (item, config) => (
  <div className="list-item-content">
    <div className="list-item-fields">
      {config.paragraphs.map((fieldObj, index) => (
        <div className="list-item-paragraph-wrapper" key={index}>
          <label className={`list-item-label list-item-label-${index}`}>
            {fieldObj.label}
          </label>
          <p className={`list-item-paragraph list-item-paragraph-${index}`}>
            {item[fieldObj.key]}
          </p>
        </div>
      ))}
    </div>
    <div className="list-item-links">
      {config.links &&
        config.links.map((linkConfig, index) => (
          <div className="list-item-link-wrapper" key={index}>
            <Link
              className={`list-item-link list-item-link-${index}`}
              to={`${linkConfig.linkPrefix}${item[linkConfig.link]}`}
            >
              {linkConfig.linkText}
            </Link>
          </div>
        ))}
    </div>
  </div>
);

const ListRenderer = ({
  items,
  itemTitles, // New prop for list-item titles
  keyExtractor,
  title,
  listClassName,
  itemClassName,
  renderContent = defaultRenderContent,
  contentConfig,
}) => {
  return (
    <div
      className={`list-container ${listClassName}`}
      id={`${title.toLowerCase().replace(' ', '-')}-list-container`}
    >
      <h1
        id={`${title.toLowerCase().replace(' ', '-')}-list-title`}
        className="list-title"
      >
        {title}
      </h1>
      <div className="list-items">
        {items.map((item, index) => (
          <div
            key={keyExtractor(item, index)}
            className={`list-item ${itemClassName}`}
            id={`${title.toLowerCase().replace(' ', '-')}-list-item-${index}`}
          >
            {/* Adding title for each list-item */}
            {itemTitles && itemTitles[index] && (
              <h3 className="list-item-individual-title">
                {itemTitles[index]}
              </h3>
            )}
            {renderContent(item, contentConfig)}
          </div>
        ))}
      </div>
    </div>
  );
};

ListRenderer.propTypes = {
  items: PropTypes.array.isRequired,
  keyExtractor: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  listClassName: PropTypes.string,
  itemClassName: PropTypes.string,
  renderContent: PropTypes.func,
  itemTitles: PropTypes.arrayOf(PropTypes.string),
  contentConfig: PropTypes.shape({
    title: PropTypes.string.isRequired,
    paragraphs: PropTypes.arrayOf(PropTypes.object).isRequired,
    links: PropTypes.arrayOf(
      PropTypes.shape({
        link: PropTypes.string.isRequired,
        linkPrefix: PropTypes.string.isRequired,
        linkText: PropTypes.string.isRequired,
      }),
    ).isRequired,
  }).isRequired,
};

ListRenderer.defaultProps = {
  listClassName: '',
  itemClassName: '',
  renderContent: defaultRenderContent,
  itemTitles: null,
};

export default ListRenderer;
