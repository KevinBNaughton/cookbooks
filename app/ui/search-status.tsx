"use client";

import { useSearchParams, usePathname, useRouter } from "next/navigation";
import { useDebouncedCallback } from "use-debounce";
import ToggleButton from "@mui/material/ToggleButton";
import ToggleButtonGroup from "@mui/material/ToggleButtonGroup";

export default function SearchStatus({ status }: { status: string }) {
  const searchParams = useSearchParams();
  const pathname = usePathname();
  const { replace } = useRouter();
  const handleStatusChange = useDebouncedCallback(
    (_event: React.MouseEvent<HTMLElement>, newStatus: string) => {
      const params = new URLSearchParams(searchParams);
      params.set("page", "1");
      if (newStatus) {
        params.set("status", newStatus);
      } else {
        params.delete("status");
      }
      replace(`${pathname}?${params.toString()}`);
    },
    300,
  );

  return (
    <div className="relative flex flex-1 flex-shrink-0">
      <ToggleButtonGroup
        color="primary"
        value={status}
        exclusive
        onChange={handleStatusChange}
        aria-label="Status"
      >
        <ToggleButton value="">All</ToggleButton>
        <ToggleButton value="uncooked">uncooked</ToggleButton>
        <ToggleButton value="cooked!">cooked~</ToggleButton>
      </ToggleButtonGroup>
    </div>
  );
}
