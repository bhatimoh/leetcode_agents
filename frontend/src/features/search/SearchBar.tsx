import type { FormEvent } from "react";

type SearchBarProps = {
  username: string;
  busy: boolean;
  onUsernameChange: (value: string) => void;
  onSubmit: () => void;
};

export function SearchBar({ username, busy, onUsernameChange, onSubmit }: SearchBarProps) {
  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit();
  }

  return (
    <form className="search" onSubmit={handleSubmit}>
      <label htmlFor="username">LeetCode username</label>
      <div className="search-row">
        <input
          id="username"
          name="username"
          autoComplete="off"
          placeholder="e.g. mohan"
          value={username}
          disabled={busy}
          onChange={(event) => onUsernameChange(event.target.value)}
        />
        <button type="submit" disabled={busy || username.trim().length === 0} aria-busy={busy}>
          {busy ? "Analyzing" : "Analyze"}
        </button>
      </div>
    </form>
  );
}
