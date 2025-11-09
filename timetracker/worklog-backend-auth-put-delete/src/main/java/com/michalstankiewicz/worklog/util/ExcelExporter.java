package com.michalstankiewicz.worklog.util;

import com.michalstankiewicz.worklog.model.Worklog;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.util.List;

public class ExcelExporter {

    public static ByteArrayInputStream worklogsToExcel(List<Worklog> worklogs) throws IOException {
        String[] columns = {
            "ID",
            "Data",
            "Imię",
            "Nazwisko",
            "Czas pracy (h)",
            "Posiłki",
            "Noclegi"
        };
        try (Workbook workbook = new XSSFWorkbook(); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            Sheet sheet = workbook.createSheet("Wpisy godzinowe");

            // Header row style
            Font headerFont = workbook.createFont();
            headerFont.setBold(true);
            CellStyle headerCellStyle = workbook.createCellStyle();
            headerCellStyle.setFont(headerFont);

            // Header row
            Row headerRow = sheet.createRow(0);
            for (int i = 0; i < columns.length; i++) {
                Cell cell = headerRow.createCell(i);
                cell.setCellValue(columns[i]);
                cell.setCellStyle(headerCellStyle);
            }

            // Data rows
            int rowIdx = 1;
            for (Worklog worklog : worklogs) {
                Row row = sheet.createRow(rowIdx++);

                row.createCell(0).setCellValue(worklog.getId());
                row.createCell(1).setCellValue(worklog.getWorkDate().toString());
                row.createCell(2).setCellValue(worklog.getUser() != null ? worklog.getUser().getName() : "N/A");
                row.createCell(3).setCellValue(worklog.getUser() != null ? worklog.getUser().getSurname() : "N/A");
                row.createCell(4).setCellValue(worklog.getTimeSpent() != null ? worklog.getTimeSpent().doubleValue() : 0.0);
                row.createCell(5).setCellValue(worklog.getMealsOrdered());
                row.createCell(6).setCellValue(worklog.getNightsSpent());
            }

            // Auto-size columns
            for (int i = 0; i < columns.length; i++) {
                sheet.autoSizeColumn(i);
            }

            workbook.write(out);
            return new ByteArrayInputStream(out.toByteArray());
        }
    }
}

