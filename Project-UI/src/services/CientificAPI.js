import httpCommon from "../http-common"

const generateReport = (data) => {
    return httpCommon.post("/generate-report/", data);
}

const latexReport = (data) => {
    return httpCommon.post("/generate-report-pdf/", data);
}


export default generateReport; latexReport;