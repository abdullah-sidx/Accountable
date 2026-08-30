import { createFileRoute } from "@tanstack/react-router";
// @ts-expect-error - JSX app lives in the frontend/ directory
import App from "../../frontend/src/App.jsx";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Accountable — Civic Transparency Platform" },
      {
        name: "description",
        content:
          "Report civic problems with photos and GPS, track the money from sanction to work done, and earn civic recognition.",
      },
      { property: "og:title", content: "Accountable — Civic Transparency Platform" },
      {
        property: "og:description",
        content:
          "A live city issue heatmap, citizen photo reports, and a public fund trail from sanction to verified work.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: App,
});
