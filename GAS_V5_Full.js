function doPost(e) {
    var lock = LockService.getScriptLock();
    lock.tryLock(10000);

    try {
        var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
        var jsonData = JSON.parse(e.postData.contents);
        var action = jsonData.action || "upload"; // Default to upload if not specified

        // --- Action 1: Upload Data & Image ---
        if (action == "upload") {
            var folderId = jsonData.folder_id || "root"; // Use provided ID or default to root
            var imageUrl = "";

            // 1. Handle Image Upload (if exists)
            if (jsonData.image_base64 && jsonData.image_base64.length > 0) {
                var decoded = Utilities.base64Decode(jsonData.image_base64);
                var blob = Utilities.newBlob(decoded, "image/jpeg", jsonData.filename);
                var folder = DriveApp.getFolderById(folderId);
                var file = folder.createFile(blob);
                file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
                // imageUrl = file.getId(); 
                imageUrl = "https://drive.google.com/file/d/" + file.getId() + "/view?usp=sharing"; // Save full link
            }

            // 2. Parse Status (Crucial Fix)
            // If Python sends strict status (e.g. "結案"), use it. Otherwise default to "未審核".
            var status = jsonData.status || "未審核";

            // 3. Append to Sheet
            // Order: [Timestamp, Model, PartNo, PartName, Type, Weight, Length, Material, ChangePoint, ActionTaken, Status, Comment, Result, Image]
            sheet.appendRow([
                jsonData.timestamp,
                jsonData.model,
                jsonData.part_no,
                jsonData.part_name,    // Index 3
                jsonData.inspection_type,
                jsonData.weight,
                jsonData.length,
                jsonData.material_ok,
                jsonData.change_point,
                jsonData.action_taken, // <--- [New] Action Taken (Index 9 / Column J)
                status,                // Index 10
                "",                    // Manager Comment (Index 11, Empty initially)
                jsonData.result,       // Index 12
                imageUrl               // Index 13
            ]);

            return ContentService.createTextOutput(JSON.stringify({
                "status": "Success",
                "message": "Data uploaded successfully",
                "image_url": imageUrl
            })).setMimeType(ContentService.MimeType.JSON);
        }

        // --- Action 2: Get All Data ---
        else if (action == "get_all_data") {
            var rows = sheet.getDataRange().getDisplayValues(); // Use getDisplayValues for strings
            var data = [];

            for (var i = 1; i < rows.length; i++) {
                var row = rows[i];
                var record = {};

                // [Fix] Schema Compatibility Check
                // New Schema (14 cols): ..., ActionTaken(9), Status(10), Comment(11), Result(12), Image(13)
                // Old Schema (13 cols): ..., Status(9), Comment(10), Result(11), Image(12)

                // Heuristic: Check by total length or specific column content
                // If row has 14 columns (or more) and row[13] is likely Image URL (http...), it's New Schema.
                // Or if row[12] is Image URL, it's Old Schema (V4).

                // Since user manually inserts column, row length should be uniform > 9.
                // We assume V5 structure for all rows now.

                record['timestamp'] = row[0];
                record['model'] = row[1];
                record['part_no'] = row[2];
                record['part_name'] = row[3];
                record['inspection_type'] = row[4];
                record['weight'] = row[5];
                record['length'] = row[6];
                record['material_ok'] = row[7];
                record['change_point'] = row[8];
                record['action_taken'] = row[9]; // [New]
                record['status'] = row[10];
                record['manager_comment'] = row[11];
                record['result'] = row[12];
                record['image'] = row[13];

                data.push(record);
            }

            return ContentService.createTextOutput(JSON.stringify({
                "status": "Success",
                "data": data
            })).setMimeType(ContentService.MimeType.JSON);
        }


        // --- Action 4: Get History (Filtered by Part No) ---
        else if (action == "get_history") {
            var targetPart = jsonData.part_no;
            var rows = sheet.getDataRange().getDisplayValues(); // Use DisplayValues for consistency
            var data = [];

            for (var i = 1; i < rows.length; i++) {
                var row = rows[i];
                // Check Part No match (Column Index 2)
                if (row[2] == targetPart) {
                    var record = {};
                    record['timestamp'] = row[0];
                    record['model'] = row[1];
                    record['part_no'] = row[2];
                    // Skip PartName (row[3]) for local history object unless needed
                    record['inspection_type'] = row[4];
                    record['weight'] = row[5];
                    record['length'] = row[6];
                    record['change_point'] = row[8];
                    record['action_taken'] = row[9]; // [New]
                    record['status'] = row[10];
                    record['manager_comment'] = row[11];
                    record['result'] = row[12];
                    record['image'] = row[13];
                    data.push(record);
                }
            }

            return ContentService.createTextOutput(JSON.stringify({
                "status": "Success",
                "data": data
            })).setMimeType(ContentService.MimeType.JSON);
        }

        // --- Action 3: Update Status ---
        else if (action == "update_status") {
            var targetTs = jsonData.timestamp;
            var targetPart = jsonData.part_no;
            var newStatus = jsonData.status;
            var newComment = jsonData.manager_comment;
            var newCP = jsonData.change_point; // [Feature] Allow updating Change Point content
            var applyAll = jsonData.apply_all; // [Feature] Batch Update Flag

            var rows = sheet.getDataRange().getDisplayValues();
            var updatedCount = 0;

            for (var i = 1; i < rows.length; i++) {
                var sheetDateStr = rows[i][0];
                var sheetPart = rows[i][2];

                var isTimeMatch = (sheetDateStr == targetTs);
                var isPartMatch = (sheetPart == targetPart);

                if (isTimeMatch && (applyAll || isPartMatch)) {
                    // Update Change Point (Col I -> index 8)
                    if (newCP !== undefined) {
                        sheet.getRange(i + 1, 9).setValue(newCP);
                    }

                    // Update Status (Col K -> index 10) [Shifted +1]
                    sheet.getRange(i + 1, 11).setValue(newStatus);
                    // Update Comment (Col L -> index 11) [Shifted +1]
                    sheet.getRange(i + 1, 12).setValue(newComment);
                    updatedCount++;

                    if (!applyAll) break; // Stop if strictly one
                }
            }

            if (updatedCount > 0) {
                return ContentService.createTextOutput(JSON.stringify({
                    "status": "Success",
                    "message": "Updated " + updatedCount + " rows"
                })).setMimeType(ContentService.MimeType.JSON);
            } else {
                return ContentService.createTextOutput(JSON.stringify({
                    "status": "Error",
                    "message": "Row not found"
                })).setMimeType(ContentService.MimeType.JSON);
            }
        }

    } catch (e) {
        return ContentService.createTextOutput(JSON.stringify({
            "status": "Error",
            "message": e.toString()
        })).setMimeType(ContentService.MimeType.JSON);
    } finally {
        lock.releaseLock();
    }
}
