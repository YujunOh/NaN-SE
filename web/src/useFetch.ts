import { useEffect, useState } from "react";

interface State<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
}

// 단순 read fetch 훅. deps가 바뀌면 다시 부른다.
export function useFetch<T>(fn: () => Promise<T>, deps: unknown[] = []): State<T> {
  const [state, setState] = useState<State<T>>({
    data: null,
    error: null,
    loading: true,
  });

  useEffect(() => {
    let alive = true;
    setState({ data: null, error: null, loading: true });
    fn()
      .then((data) => alive && setState({ data, error: null, loading: false }))
      .catch((e) => alive && setState({ data: null, error: String(e), loading: false }));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return state;
}
