# Risk Mitigation Strategy GIS Tool
## Overview
The project “Risk Mitigation Strategy” stems out of a collaboration of ETH Zurich, the Swiss
Development Cooperation (SDC), and UNHCR through the Geneva Technical Hub initiative
(GTH). The aim of the project is to support field staff in identifying and mapping flood risks for a
given refugee settlement and provide general guidance on adapted mitigation measures. The
project comprises three parts: 1) a GIS tool, 2) a compendium of risk mitigation measures for
refugee settlements, and 3) local data collection guide and other supporting documents.

The project includes an easy-to-use GIS tool to create an operational and practical flood risk
mitigation strategy for refugee settlements, combining local and global data. The extension (Plug-
In), developed for the open source QGIS application, supports field staff in mapping and analyzing
flood risk and vulnerable assets. Additionally, the tool helps identifying mitigation measures
adapted to the context and operational priorities. The step-by-step process is divided in four main
tasks: hazard mapping, vulnerability mapping, risk mapping and identification of mitigation
measures. The outcome provides support for deciding on the most suitable risk
mitigation strategy, including a risk map and a range of appropriate risk mitigation measures.

This repository contains the source code (`source-code/`), the user manual and tutorial (`docs/`) as well as a ready-to-use ZIP file (`risk-mitigation-qgis-plugin.zip`) of the Risk Mitigation Strategy GIS Tool. You can find more information about the project, resources for the other project components, and learning materials for the GIS tool at: https://humanitarian-risk.unhcr.org/index.php.

### When to use the Risk Mitigation Strategy Tool
This tool helps combining hazard and vulnerability mapping, leading to a risk map and to a risk
mitigation strategy with adequate risk mitigation measures. Its strength lies in the combination of
local and global data and ease of use. However, in certain scenarios, the benefit of using the tool
is diminished:
- The tool works best when there is global data input (automated) with added local data on
flood hazards. If there is no local data on flood hazards, the quality of the outcome will be
lower. At the same time, if global data shows no flood hazard, the risk map will be entirely
based on the manual input. The tool will still provide meaningful results in both cases.
- The tool helps to prioritize mitigation measures. If the entire settlement area is equally
affected by the same hazard with the same frequency and intensity, the tool provides
prioritization only based on vulnerability mapping but no spatialized prioritization. In this
case, it might be better to directly refer to the catalog of risk mitigation measures without
using the tool.
- If there is no flood hazard in the settlement, this tool is not helpful, as it focuses solely on
floods and no other natural hazards.

## Using the Tool
### Compatibility
The plugin has been developed for QGIS 3.28 LTR. We recommend using this long-term release
version of QGIS, as it offers optimal stability and compatibility with the plugin.

### Installation
1. Download the ZIP file `risk-mitigation-qgis-plugin.zip` to your device.
2. Open QGIS, navigate to `Plugins` >  `Manage and Install Plugins`.
3. Click on `Install from ZIP`, select the downloaded ZIP folder and press `Install Plugin`.
4. Click `yes` if a security warning appears.
5. Return to `Plugins` >  `Installed` and check the box next to "UNHCR Risk Mapping". Ensure that the "Processing" plugin is also selected.

### Setting up the Project
> ⚠️ Important: The tool must be used with the provided QGIS project file (`UNHCR.qgz`).
It includes required layers, styling, and pre-configured settings.

1. Download the `base-project.zip` folder to your device and extract its contents.
2. Open QGIS and load the supplied project (`UNHCR.qgz`)
3. Upon loading the `UNHCR.qgz` project, you should observe a map and preloaded data in the Layers panel.
4. Start the tool by pressing `1` in the toolbar.


## How to cite
Rohling, Bruna; Kostenwein, David; Gairing, Mona; Nimri, Rama; Al-Mahdawi, Ammar; Schmid, Emilie; Bardou, Eric; Kaufmann, David (2023) Flood Risk in Humanitarian Settlements: Compendium of Mitigation Measures. Zurich: ETH Zürich, UNHCR. DOI: 10.3929/ethz-b-000645680

## Contact Information
For questions, feedback, or support, please reach out to ...
