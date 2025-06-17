import httpCommon from "../http-common"

const generateReport = (data) => {
  console.log("Datos enviados para generar el reporte:", data);
  return httpCommon.post("/generate-report/", data, {
    headers: {
      "Content-Type": "application/json"
    }
  });
};

const latexReport = (data) => {
  console.log("Datos enviados para generar el reporte en LaTeX:", data);
  return httpCommon.post("/generate-and-download-pdf/", data, {
    headers: {
      "Content-Type": "application/json"
    }
  });
};


export default generateReport; latexReport;