/**
 * Encuesta module color tokens.
 *
 * One place to change colors for the entire encuesta module across all roles.
 *
 * Usage:
 *   import { ENCUESTA_COLORS } from "@/lib/encuesta-colors";
 *   className={ENCUESTA_COLORS.worker.button}
 */

export const BUTTONS_COLORS = {
  /**
   * Worker & PM: soft lavender buttons.
   * Used in all interactive buttons inside the encuesta flow.
   */
  worker: {
    /** Standard button background */
    button: "bg-[#E0D7F9] text-foreground hover:bg-[#cfc4f5]",
    /** Active / selected state (e.g. a scale option the user picked) */
    buttonActive: "bg-[#E0D7F9] text-foreground border-[#cfc4f5]",
    /** Pending survey list items */
    listItem: "bg-[#E0D7F9] text-foreground hover:bg-[#cfc4f5]",
  },

  /**
   * PM mirrors worker exactly — same palette, kept as a named alias
   * so future divergence only requires changing this entry.
   */
  get pm() {
    return this.worker;
  },

  /**
   * HR: darker slate-blue buttons in the main view.
   * Modals inside HR use the lighter worker palette (see hrModal below).
   */
  hr: {
    button: "bg-[#8795C7] text-white hover:bg-[#7485bb]",
    buttonActive: "bg-[#8795C7] text-white border-[#7485bb]",
    listItem: "bg-[#8795C7] text-white hover:bg-[#7485bb]",
  },

  /**
   * HR modals / dialogs: revert to the lighter lavender inside pop-ups.
   */
  hrModal: {
    button: "bg-[#E0D7F9] text-foreground hover:bg-[#cfc4f5]",
    buttonActive: "bg-[#E0D7F9] text-foreground border-[#cfc4f5]",
  },
} as const;
