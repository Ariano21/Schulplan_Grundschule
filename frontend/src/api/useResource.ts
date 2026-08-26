import { useCallback, useEffect, useState } from "react";
import { api, ApiError } from "./client";

interface WithId {
  id: number;
}

export function useResource<T extends WithId, TCreate>(path: string) {
  const [items, setItems] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    setLoading(true);
    api
      .get<T[]>(path)
      .then(setItems)
      .catch((err: unknown) => setError(err instanceof ApiError ? err.message : "Laden fehlgeschlagen."))
      .finally(() => setLoading(false));
  }, [path]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  async function create(payload: TCreate): Promise<void> {
    setError(null);
    try {
      const created = await api.post<T>(path, payload);
      setItems((prev) => [...prev, created]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Anlegen fehlgeschlagen.");
      throw err;
    }
  }

  async function remove(id: number): Promise<void> {
    setError(null);
    try {
      await api.delete(`${path}/${id}`);
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Löschen fehlgeschlagen.");
      throw err;
    }
  }

  return { items, loading, error, create, remove, refresh };
}
