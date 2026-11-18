/** @odoo-module **/
// Copyright 2026 Biricon IT Services GmbH
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import { patch } from "@web/core/utils/patch";
import { SectionAndNoteListRenderer } from "@account/components/section_and_note_fields_backend/section_and_note_fields_backend";

// Moving a section (e.g. a product set) sometimes ended in
// "TypeError: Cannot read properties of undefined (reading 'data')": after the drop the dragged
// record is no longer found in the list (its id changed while the list was re-sorted/saved), and
// the standard code reads `record.data` without checking. Nothing is left to reset in that case.
patch(SectionAndNoteListRenderer.prototype, {
    resetOnResequence(record, parentSection) {
        if (!record) {
            return false;
        }
        return super.resetOnResequence(record, parentSection);
    },
});
