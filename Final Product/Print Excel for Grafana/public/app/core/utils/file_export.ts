///<reference path="../../headers/common.d.ts" />

import _ from 'lodash';
//import * as XLSX from 'XLSX';
import * as Excel from 'excel';
declare var window: any;
declare function require (path: string): any;

export function exportTableDataToXML(table){
    var title = [];
    var titleCount = 0;
    var ep = new Excel.ExcelPlus();
    ep.createFile("Grafana");
    _.each(table.columns, function(column) {
        title[titleCount++] = column.text;
    });
    //Write titles
    ep.write({ "content": [title] });
    //Write data
    _.each(table.rows, function(row) {
        var data = [];
        var dataCount = 0;
        _.each(row, function(value) {
            if (dataCount === 0){
                data[dataCount++] = convertTime(value);
            } else {
                data[dataCount++] = value;
            }
        });
        ep.writeNextRow(data);
    });
    try {
      ep.saveAs("Table_Data.xlsx");
    } catch (e){
      alert("Table_Data_Error");
    }
};

function convertTime(dp){
    var tzOffset = new Date().getTimezoneOffset()/(-60);
    var bf = dp;
    dp = dp + (tzOffset*3600*1000);
    var str = new Date(dp).toISOString();
    var yyyy = str.substring(0,4);
    var mm = str.substring(5,7);
    var dd = str.substring(8,10);
    var hr = str.substring(11,13);
    var m = str.substring(14,16);
    var ss = str.substring(17,19);
    var d = new Date (str);
    //var d = new Date(yyyy, mm-1, dd, hr, m, ss);
    //var sub = dd +"/"+ mm + "/"+ yyyy +" "+hr + ":" + m + ":" + ss;
    return d;
}

export function exportSeriesListToXML(seriesList) {

    var title = [];
    var titleCount = 0;
    var ep = new Excel.ExcelPlus();
    ep.createFile("Grafana");

    //Write title
    title[0] = "Series";
    title[1] = "Time";
    title[2] = "Value";
    ep.write({ "content": [title] });
    //Write data
    _.each(seriesList, function(series) {
        _.each(series.datapoints, function(dp) {
            var data = [];
            data[0] = series.alias;
            data[1] = convertTime(dp[1]);
            data[2] = dp[0];
            ep.writeNextRow(data);
        });
    });
    try {
      ep.saveAs("Graph_Data_Rows.xlsx");
    } catch (e){
      alert("Graph_Data_Error");
    }
};

export function exportSeriesListToXMLColumns(seriesList) {
    var title = [];
    var titleCount = 0;
    var ep = new Excel.ExcelPlus();
    ep.createFile("Grafana");
    //Write Headers
    title[titleCount++]= "Time";
    _.each(seriesList, function(series) {
        title[titleCount++] = series.alias;
    });
    ep.write({ "content": [title] });

    // process data
    var dataArr = [[]];
    var sIndex = 1;
    _.each(seriesList, function(series) {
        var cIndex = 0;
        dataArr.push([]);
        _.each(series.datapoints, function(dp) {
            dataArr[0][cIndex] = convertTime(dp[1]);
            dataArr[sIndex][cIndex] = dp[0];
            cIndex++;
        });
        sIndex++;
    });

    // make text
    for (var i = 0; i < dataArr[0].length; i++) {
        var data = [];
        var dataCount = 0;
        data[dataCount++]= dataArr[0][i];
        for (var j = 1; j < dataArr.length; j++) {
            data[dataCount++]= dataArr[j][i];
        }
        ep.writeNextRow(data);
    }
    try {
      ep.saveAs("Graph_Data_Columns.xlsx");
    } catch (e){
      alert("Graph_Data_Columns_Error");
    }
};

export function exportTableDataToCsv(table) {
    var text = '';
    // add header
    _.each(table.columns, function(column) {
        text += column.text + ',';
    });
    text += '\n';
    // process data
    _.each(table.rows, function(row) {
        _.each(row, function(value) {
            text += value + ',';
        });
        text += '\n';
    });
    saveSaveBlob(text, 'Table_Data.csv');
};

export function exportSeriesListToCsv(seriesList) {
    console.log("export Rows");
    var text = 'Series;Time;Value\n';
    _.each(seriesList, function(series) {
        _.each(series.datapoints, function(dp) {
            text += series.alias + ',' + new Date(dp[1]).toISOString() + ',' + dp[0] + '\n';
        });
    });
    saveSaveBlob(text, 'Graph_Data_Rows.csv');
};

export function exportSeriesListToCsvColumns(seriesList) {
    var text = 'Time;';
    console.log("export Column");
    // add header
    _.each(seriesList, function(series) {
        text += series.alias + ',';
    });
    text = text.substring(0,text.length-1);
    text += '\n';

    // process data
    var dataArr = [[]];
    var sIndex = 1;
    _.each(seriesList, function(series) {
        var cIndex = 0;
        dataArr.push([]);
        _.each(series.datapoints, function(dp) {
            dataArr[0][cIndex] = new Date(dp[1]).toISOString();
            dataArr[sIndex][cIndex] = dp[0];
            cIndex++;
        });
        sIndex++;
    });

    // make text
    for (var i = 0; i < dataArr[0].length; i++) {
        text += dataArr[0][i] + ',';
        for (var j = 1; j < dataArr.length; j++) {
            text += dataArr[j][i] + ',';
        }
        text = text.substring(0,text.length-1);
        text += '\n';
    }
    saveSaveBlob(text, 'Graph_Data_Columns.csv');
};

export function saveSaveBlob(payload, fname) {
    var blob = new Blob([payload], { type: "text/csv;charset=utf-8" });
    window.saveAs(blob, fname);
};

export function saveSaveBlobXLSX(payload, fname) {
    var blob = new Blob([payload], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;charset=utf-8" });
    window.saveAs(blob, fname);
};

export function saveSaveBlobXML(payload, fname) {
    var blob = new Blob([payload], { type: "text/xml;charset=utf-8" });
    window.saveAs(blob, fname);
};

export function insertXMLTail(){
    var text = '\</Table\>\n'+
          '\<WorksheetOptions xmlns\="urn\:schemas-microsoft-com\:office\:excel"\>\n'+
           '\<PageSetup\>\n'+
            '\<Header x\:Margin\="0.3"/\>\n'+
            '\<Footer x\:Margin\="0.3"/\>\n'+
            '\<PageMargins x\:Bottom\="0.75" x\:Left\="0.7" x\:Right\="0.7" x\:Top\="0.75"/>\n'+
           '\</PageSetup\>\n'+
           '\<Selected/\>\n'+
           '\<ProtectObjects\>False\</ProtectObjects\>\n'+
           '\<ProtectScenarios\>False\</ProtectScenarios\>\n'+
          '\</WorksheetOptions\>\n'+
         '\</Worksheet\>\n'+
        '\</Workbook\>\n';
    return text;
}

export function insertXMLHead() {
    var text = '\<\?xml version\="1.0"\?\>';
    text+= '\<?mso-application progid\="Excel.Sheet"?\>'+
        '\<Workbook xmlns\="urn\:schemas-microsoft-com\:office\:spreadsheet"'+
         ' xmlns\:o\="urn\:schemas-microsoft-com\:office\:office"'+
         ' xmlns\:x\="urn\:schemas-microsoft-com\:office\:excel"'+
         ' xmlns\:ss\="urn\:schemas-microsoft-com\:office\:spreadsheet"'+
         ' xmlns\:html\="http\://www.w3.org/TR/REC-html40"\>'+
         '\<DocumentProperties xmlns\="urn\:schemas-microsoft-com\:office\:office"\>'+
         '\</DocumentProperties\>'+
         '\<OfficeDocumentSettings xmlns\="urn\:schemas-microsoft-com\:office\:office"\>'+
          '\<AllowPNG/\>'+
         '\</OfficeDocumentSettings\>'+
         '\<ExcelWorkbook xmlns\="urn\:schemas-microsoft-com\:office\:excel"\>'+
          '\<WindowHeight\>9228\</WindowHeight\>'+
          '\<WindowWidth\>23040\</WindowWidth\>'+
          '\<WindowTopX\>0\</WindowTopX\>'+
          '\<WindowTopY\>0\</WindowTopY\>'+
          '\<ProtectStructure\>False\</ProtectStructure\>'+
          '\<ProtectWindows\>False\</ProtectWindows\>'+
         '\</ExcelWorkbook\>'+
         '\<Styles\>'+
          '\<Style ss\:ID\="Default" ss\:Name\="Normal"\>'+
           '\<Alignment ss\:Vertical\="Bottom"/\>'+
           '\<Borders/\>'+
           '\<Font ss\:FontName\="Calibri" x\:Family\="Swiss" ss\:Size\="11" ss\:Color\="#000000"/\>'+
           '\<Interior/\>'+
           '\<NumberFormat/\>'+
           '\<Protection/\>'+
          '\</Style\>'+
          '\<Style ss\:ID\="s62"\>'+
           '\<NumberFormat ss\:Format\="0%"/\>'+
          '\</Style\>'+
         '\</Styles\>'+
         '\<Worksheet ss\:Name\="Sheet1"\>'+
          '\<Table x\:FullColumns\="1"'+
           ' x\:FullRows\="1" ss\:DefaultRowHeight\="14.4"\>\n';
    return text;
};


