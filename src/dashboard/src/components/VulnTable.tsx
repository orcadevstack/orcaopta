import React from "react";
import { Table, TableHead, TableRow, TableCell, TableBody } from "@mui/material";

export default function VulnTable() {
  const vulns = [
    { id: 1, severity: "HIGH", component: "mlflow", cve: "CVE-2025-1234" },
    { id: 2, severity: "CRITICAL", component: "app", cve: "CVE-2026-5678" },
  ];

  return (
    <>
      <h2>Vulnerability Scan Results</h2>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Component</TableCell>
            <TableCell>Severity</TableCell>
            <TableCell>CVE</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {vulns.map((v) => (
            <TableRow key={v.id}>
              <TableCell>{v.component}</TableCell>
              <TableCell>{v.severity}</TableCell>
              <TableCell>{v.cve}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </>
  );
}
