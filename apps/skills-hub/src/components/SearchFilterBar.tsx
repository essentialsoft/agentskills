type SearchFilterBarProps = {
  query: string;
  tag: string;
  tags: string[];
  onQueryChange: (query: string) => void;
  onTagChange: (tag: string) => void;
};

export function SearchFilterBar({
  query,
  tag,
  tags,
  onQueryChange,
  onTagChange,
}: SearchFilterBarProps) {
  return (
    <section className="search-filter">
      <label>
        <span>Search skills</span>
        <input
          aria-label="Search skills"
          value={query}
          onChange={(event) => onQueryChange(event.target.value)}
          placeholder="Search by name, description, or purpose"
        />
      </label>

      <label>
        <span>Filter by tag</span>
        <select
          aria-label="Filter by tag"
          value={tag}
          onChange={(event) => onTagChange(event.target.value)}
        >
          <option value="all">All tags</option>
          {tags.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </label>
    </section>
  );
}
