import { useRef, useState } from "react";

/**
 * SnapTagForm — citizens upload a photo of a civic problem, tagged with GPS coordinates.
 *
 * Submits to:  POST http://127.0.0.1:8000/api/v1/complaints
 * Payload:     JSON matching ComplaintCreate schema
 *              { title, description, latitude, longitude, ... }
 */

const CATEGORIES = [
  "Pothole",
  "Garbage",
  "Street light",
  "Water leak",
  "Drainage",
  "Encroachment",
  "Other",
];

const BACKEND_URL = "http://127.0.0.1:8000";

export default function SnapTagForm() {
  const fileInputRef = useRef(null);
  const [photo, setPhoto] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [customCategory, setCustomCategory] = useState("");
  const [description, setDescription] = useState("");
  const [coords, setCoords] = useState(null);
  const [geoStatus, setGeoStatus] = useState("idle");
  const [submitState, setSubmitState] = useState({ status: "idle", message: "" });

  // ── Handlers ────────────────────────────────────────────────────────────────

  const handleFile = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setPhoto(file);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(URL.createObjectURL(file));
  };

  const tagLocation = () => {
    if (!navigator.geolocation) {
      setGeoStatus("unsupported");
      return;
    }
    setGeoStatus("locating");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setCoords({
          lat: Number(pos.coords.latitude.toFixed(6)),
          lng: Number(pos.coords.longitude.toFixed(6)),
          accuracy: Math.round(pos.coords.accuracy),
        });
        setGeoStatus("tagged");
      },
      () => setGeoStatus("denied"),
      { enableHighAccuracy: true, timeout: 10000 },
    );
  };

  const reset = () => {
    setPhoto(null);
    if (previewUrl) URL.revokeObjectURL(previewUrl);
    setPreviewUrl(null);
    setDescription("");
    setCategory(CATEGORIES[0]);
    setCustomCategory("");
    setCoords(null);
    setGeoStatus("idle");
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // ── Submit ───────────────────────────────────────────────────────────────────

  const onSubmit = async (event) => {
    event.preventDefault();

    // Client-side validation
    if (!photo) {
      setSubmitState({ status: "error", message: "Attach a photo of the issue first." });
      return;
    }
    if (!coords) {
      setSubmitState({ status: "error", message: "Tag GPS coordinates before submitting." });
      return;
    }

    // Resolve the final category (use free-text when "Other" is selected)
    const finalCategory = category === "Other" ? customCategory.trim() : category;
    if (category === "Other" && !customCategory.trim()) {
      setSubmitState({
        status: "error",
        message: "Please describe the category in the custom field.",
      });
      return;
    }

    // Build JSON payload matching ComplaintCreate (backend schema):
    //   title       str min_length=5   ← derived from category + coordinates
    //   description str min_length=10  ← user's "What is wrong?" text (padded if short)
    //   latitude    float              ← GPS lat
    //   longitude   float              ← GPS lng
    const title = `${finalCategory} issue at ${coords.lat}, ${coords.lng}`;
    const rawDesc = description.trim();
    const paddedDesc =
      rawDesc.length >= 10
        ? rawDesc
        : `${finalCategory} issue reported near coordinates ${coords.lat}, ${coords.lng} via the Accountable app.`;

    const payload = {
      title,
      description: paddedDesc,
      latitude: coords.lat,
      longitude: coords.lng,
      address: null,
      ward_id: null,
      submitter_name: null,
      submitter_contact: null,
      is_anonymous: false,
    };

    // POST http://127.0.0.1:8000/api/v1/complaints
    setSubmitState({ status: "submitting", message: "" });
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/complaints`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify(payload),
      });

      let data = {};
      try {
        data = await res.json();
      } catch {
        /* non-JSON body — ignore */
      }

      if (!res.ok) {
        // Surface Pydantic validation errors cleanly
        const detail =
          typeof data?.detail === "string"
            ? data.detail
            : Array.isArray(data?.detail)
              ? data.detail
                  .map((e) => `${e.loc?.slice(-1)?.[0] ?? "field"}: ${e.msg}`)
                  .join(" · ")
              : `Server error ${res.status}`;
        setSubmitState({ status: "error", message: detail });
        return;
      }

      setSubmitState({
        status: "success",
        message: `✅ Complaint filed${data?.id ? ` · Tracking ID #${data.id}` : ""}. +25 civic points!`,
      });
      reset();
    } catch {
      setSubmitState({
        status: "error",
        message:
          "Could not reach backend at http://127.0.0.1:8000. Is the FastAPI server running?",
      });
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────────

  return (
    <section className="rounded-2xl border border-border bg-card p-5 shadow-soft">
      <header>
        <h2 className="text-lg font-semibold tracking-tight text-foreground">Snap &amp; Tag</h2>
        <p className="text-sm text-muted-foreground">
          Photograph the problem, tag its exact location, and it enters the public ledger.
        </p>
      </header>

      <form onSubmit={onSubmit} className="mt-4 grid gap-4 md:grid-cols-2">
        {/* Left column — photo upload */}
        <div className="space-y-3">
          <label className="block text-sm font-medium text-foreground" htmlFor="snaptag-photo">
            Photo evidence
          </label>
          <input
            id="snaptag-photo"
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleFile}
            className="block w-full cursor-pointer rounded-xl border border-dashed border-border bg-background px-3 py-6 text-sm text-muted-foreground file:mr-3 file:rounded-lg file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-primary-foreground"
          />
          {previewUrl && (
            <img
              src={previewUrl}
              alt="Preview of the civic issue you are reporting"
              className="h-40 w-full rounded-xl object-cover"
            />
          )}
        </div>

        {/* Right column — category, description, GPS, submit */}
        <div className="space-y-3">
          {/* Category selector */}
          <div>
            <label className="block text-sm font-medium text-foreground" htmlFor="snaptag-category">
              Category
            </label>
            <select
              id="snaptag-category"
              value={category}
              onChange={(e) => {
                setCategory(e.target.value);
                if (e.target.value !== "Other") setCustomCategory("");
              }}
              className="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm text-foreground outline-none focus:border-primary"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>

            {/* Conditional "Other" free-text input — smooth slide-in */}
            <div
              className={`overflow-hidden transition-all duration-200 ${
                category === "Other" ? "mt-2 max-h-24 opacity-100" : "max-h-0 opacity-0"
              }`}
            >
              <label
                className="block text-xs font-medium text-muted-foreground"
                htmlFor="snaptag-custom-category"
              >
                Describe the category
              </label>
              <input
                id="snaptag-custom-category"
                type="text"
                value={customCategory}
                onChange={(e) => setCustomCategory(e.target.value)}
                placeholder="e.g. Fallen tree, broken bench…"
                maxLength={80}
                aria-label="Custom category description"
                className="mt-1 w-full rounded-xl border border-input bg-background px-3 py-2 text-sm text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
              />
            </div>
          </div>

          {/* Description textarea */}
          <div>
            <label className="block text-sm font-medium text-foreground" htmlFor="snaptag-desc">
              What is wrong?
            </label>
            <textarea
              id="snaptag-desc"
              rows={3}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Half the road has collapsed near the bus stop; two-wheelers are skidding."
              className="mt-1 w-full resize-none rounded-xl border border-input bg-background px-3 py-2 text-sm text-foreground outline-none placeholder:text-muted-foreground focus:border-primary"
            />
          </div>

          {/* GPS tag */}
          <div className="rounded-xl bg-muted p-3">
            <div className="flex items-center justify-between gap-3">
              <div className="text-sm">
                <p className="font-medium text-foreground">GPS tag</p>
                <p className="text-xs text-muted-foreground">
                  {coords
                    ? `${coords.lat}, ${coords.lng} (±${coords.accuracy}m)`
                    : geoStatus === "denied"
                      ? "Location permission denied"
                      : geoStatus === "unsupported"
                        ? "Geolocation unsupported on this device"
                        : "Not tagged yet"}
                </p>
              </div>
              <button
                type="button"
                onClick={tagLocation}
                className="rounded-lg border border-primary px-3 py-1.5 text-xs font-semibold text-primary transition-colors hover:bg-primary hover:text-primary-foreground"
              >
                {geoStatus === "locating" ? "Locating…" : coords ? "Re-tag" : "Tag location"}
              </button>
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={submitState.status === "submitting"}
            className="w-full rounded-xl bg-primary px-4 py-2.5 text-sm font-semibold text-primary-foreground shadow-soft transition-opacity hover:opacity-90 disabled:opacity-60"
          >
            {submitState.status === "submitting" ? "Filing report…" : "Submit report"}
          </button>

          {/* Status message */}
          {submitState.message && (
            <p
              className={`text-xs ${
                submitState.status === "error" ? "text-destructive" : "text-success"
              }`}
              role="status"
            >
              {submitState.message}
            </p>
          )}
        </div>
      </form>
    </section>
  );
}
