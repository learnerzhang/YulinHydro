from dataclasses import dataclass
from typing import Optional, List


@dataclass
class DaAgriDisasterDroughtResistRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.daagridisasterdroughtresist.vo.DaAgriDisasterDroughtResistRespVO
    
    DaAgriDisasterDroughtResistRespVO
    """
    """作物累计受灾面积"""
    drought_damage_area: Optional[float] = None
    """本年度投入抗旱人数"""
    drought_response_people: Optional[int] = None
    """其中成灾面积"""
    drought_severe_damage_area: Optional[float] = None
    """其中绝收面积"""
    drought_total_loss_area: Optional[float] = None
    """其中经济作物"""
    economic_crop_area: Optional[float] = None
    """本年度经济作物因旱损失"""
    economic_crop_loss: Optional[float] = None
    """全年抗旱减灾效益 - 其中挽回经济作物损失"""
    economic_recovery: Optional[str] = None
    """累计投入抗旱资金 - 各级财政拨款"""
    fund_local: Optional[float] = None
    """累计投入抗旱资金 - 中央拨款"""
    fund_national: Optional[float] = None
    """其中粮食作物"""
    grain_crop_area: Optional[float] = None
    """本年度粮食因旱损失"""
    grain_loss: Optional[float] = None
    """全年抗旱减灾效益 - 其中挽回粮食损失-吨"""
    grain_recovery_ton: Optional[str] = None
    """全年抗旱减灾效益 - 其中挽回粮食损失-元"""
    grain_recovery_yuan: Optional[str] = None
    """主键ID"""
    id: Optional[int] = None
    """累计完成抗旱浇灌面积-公顷次"""
    irrigated_area_ha_times: Optional[float] = None
    """累计完成抗旱浇灌面积-公顷"""
    irrigated_area_hectares: Optional[float] = None
    """本年度投入抗旱设施 - 机动抗旱设备"""
    irrigation_equipment: Optional[int] = None
    """本年度投入抗旱设施 - 泵站"""
    irrigation_stations: Optional[int] = None
    """本年度投入抗旱设施 - 机动运水车辆"""
    irrigation_vehicles: Optional[int] = None
    """本年度投入抗旱设施 - 机电井"""
    irrigation_wells: Optional[int] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区"""
    region_name: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None
    """累计解决因旱人畜饮水困难 - 大牲畜"""
    resolved_livestock: Optional[float] = None
    """累计解决因旱人畜饮水困难 - 人口"""
    resolved_population: Optional[float] = None
    """本年度累计播种面积"""
    total_crop_area: Optional[float] = None
    """作物累计受旱面积"""
    total_drought_affected_area: Optional[float] = None
    """累计投入抗旱资金 - 合计"""
    total_drought_fund: Optional[float] = None
    """本年度粮食总产量"""
    total_grain_production: Optional[float] = None
    """累计因旱人畜饮水困难 - 大牲畜"""
    water_shortage_livestock: Optional[float] = None
    """累计因旱人畜饮水困难 - 人口"""
    water_shortage_population: Optional[float] = None


@dataclass
class DaAgriDroughtDynamicRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.daagridroughtdynamic.vo.DaAgriDroughtDynamicRespVO
    
    DaAgriDroughtDynamicRespVO
    """
    """在田作物面积"""
    cropped_area: Optional[float] = None
    """作物受旱面积 - 合计"""
    drought_affected_area_total: Optional[float] = None
    """干枯"""
    drought_dead_area: Optional[float] = None
    """轻旱"""
    drought_light_area: Optional[float] = None
    """其他"""
    drought_other_area: Optional[float] = None
    """重旱"""
    drought_severe_area: Optional[float] = None
    """主键ID"""
    id: Optional[int] = None
    """牧区受旱面积"""
    pasture_drought_area: Optional[float] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区"""
    region_name: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None
    """水库干涸"""
    reservoir_dry_count: Optional[int] = None
    """水利工程蓄水情况 - 比多年同期增减"""
    reservoir_storage_change_percent: Optional[float] = None
    """水利工程蓄水情况 - 蓄水总量"""
    reservoir_storage_total: Optional[float] = None
    """河道断流"""
    river_dry_count: Optional[int] = None
    """其中无抗旱条件面积"""
    unconditional_drought_area: Optional[float] = None
    """缺水缺墒面积 - 旱地缺墒"""
    water_shortage_dryland: Optional[float] = None
    """因旱人畜饮水困难 - 大牲畜"""
    water_shortage_livestock: Optional[float] = None
    """缺水缺墒面积 - 水田缺水"""
    water_shortage_paddy: Optional[float] = None
    """因旱人畜饮水困难 - 人口"""
    water_shortage_population: Optional[float] = None
    """机电井出水不足"""
    well_low_water_count: Optional[int] = None


@dataclass
class DaAgriDroughtResistRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.daagridroughtresist.vo.DaAgriDroughtResistRespVO
    
    DaAgriDroughtResistRespVO
    """
    """本季作物实际播种面积"""
    current_crop_planned_area: Optional[float] = None
    """受旱面积合计"""
    current_drought_area_total: Optional[float] = None
    """特旱"""
    current_drought_extreme_area: Optional[float] = None
    """轻旱"""
    current_drought_light_area: Optional[float] = None
    """中旱"""
    current_drought_moderate_area: Optional[float] = None
    """重旱"""
    current_drought_severe_area: Optional[float] = None
    """旱地缺墒"""
    dryland_soil_dryness: Optional[float] = None
    """各级财政拨款"""
    fund_local_government: Optional[float] = None
    """群众自筹"""
    fund_self_raised: Optional[float] = None
    """主键ID"""
    id: Optional[int] = None
    """累计完成抗旱浇灌面积 - 千公顷次"""
    irrigated_area_ha_times: Optional[float] = None
    """累计完成抗旱浇灌面积 - 千公顷"""
    irrigated_area_hectares: Optional[float] = None
    """机动抗旱设备"""
    irrigation_equipment: Optional[int] = None
    """泵站"""
    irrigation_stations: Optional[int] = None
    """机动运水车辆"""
    irrigation_vehicles: Optional[int] = None
    """统计时段投入抗旱设施 - 机电井"""
    irrigation_wells: Optional[int] = None
    """本季作物最大受旱面积"""
    max_drought_affected_area: Optional[float] = None
    """水田缺水"""
    paddy_water_shortage: Optional[float] = None
    """牧区草场受旱面积"""
    pasture_drought_area: Optional[float] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区"""
    region_name: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None
    """统计时段投入抗旱人数"""
    report_period_people: Optional[int] = None
    """累计解决因旱人畜饮水困难 - 大牲畜"""
    resolved_livestock: Optional[float] = None
    """累计解决因旱人畜饮水困难 - 人口"""
    resolved_population: Optional[float] = None
    """响应级别"""
    response_level: Optional[str] = None
    """累计投入抗旱资金 - 合计"""
    total_drought_fund: Optional[float] = None
    """待播耕地缺水缺墒面积合计"""
    unplanted_land_area: Optional[float] = None
    """因旱人畜饮水困难 - 大牲畜"""
    water_shortage_livestock: Optional[float] = None
    """因旱人畜饮水困难 - 人口"""
    water_shortage_population: Optional[float] = None


@dataclass
class DaAgriDroughtResistOnlyRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.daagridroughtresistonly.vo.DaAgriDroughtResistOnlyRespVO
    
    DaAgriDroughtResistOnlyRespVO
    """
    """抗旱用电"""
    electricity_used: Optional[float] = None
    """装机容量"""
    equipment_capacity: Optional[float] = None
    """抗旱用油"""
    fuel_used: Optional[float] = None
    """地县级财政拨款"""
    fund_city_county: Optional[float] = None
    """中央拨款"""
    fund_national: Optional[float] = None
    """省级财政拨款"""
    fund_provincial: Optional[float] = None
    """群众自筹"""
    fund_self_raised: Optional[float] = None
    """主键ID"""
    id: Optional[int] = None
    """抗旱浇灌面积 - 千公顷次"""
    irrigated_area_ha_times: Optional[float] = None
    """抗旱浇灌面积 - 千公顷"""
    irrigated_area_hectares: Optional[float] = None
    """机动抗旱设备"""
    irrigation_equipment: Optional[int] = None
    """泵站"""
    irrigation_stations: Optional[int] = None
    """机电井"""
    irrigation_wells: Optional[int] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区"""
    region_name: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None
    """临时解决人畜饮水困难 - 大牲畜"""
    resolved_livestock: Optional[float] = None
    """临时解决人畜饮水困难 - 人口"""
    resolved_population: Optional[float] = None
    """投入抗旱人数"""
    response_people: Optional[float] = None
    """投入抗旱资金 - 合计"""
    total_fund: Optional[float] = None
    """机动运水车辆"""
    water_vehicles: Optional[int] = None


@dataclass
class DaDisasterReportTemplateRespVO:
    """模板信息
    
    DaDisasterReportTemplateRespVO
    """
    """创建时间"""
    create_time: Optional[str] = None
    """灾害类型  0=洪涝灾害，1=旱灾，2=山洪灾害"""
    disaster_type: Optional[str] = None
    """备案机关"""
    filing_agency: Optional[str] = None
    """备案文号"""
    filing_document_number: Optional[str] = None
    """制定机关"""
    formulating_agency: Optional[str] = None
    """主键ID"""
    id: Optional[int] = None
    """逻辑删除标记"""
    is_deleted: Optional[int] = None
    """报告期别"""
    report_period_types: Optional[str] = None
    """表号"""
    table_number: Optional[str] = None
    """模板名称"""
    template_name: Optional[str] = None
    """有效期至"""
    valid_until: Optional[str] = None


@dataclass
class DaFloodDisasterStatisticsInfoRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.daflooddisasterstatisticsinfo.vo.DaFloodDisasterStatisticsInfoRespVO
    
    DaFloodDisasterStatisticsInfoRespVO
    """
    """受灾县（市、区）数"""
    affected_counties: Optional[int] = None
    """受灾人口  单位：万人"""
    affected_population: Optional[float] = None
    """受灾乡（镇、街道）数"""
    affected_townships: Optional[int] = None
    """创建时间"""
    create_time: Optional[str] = None
    """农作物受灾面积  单位：千公顷"""
    crop_damage_area: Optional[float] = None
    """因灾死亡人口"""
    deaths: Optional[int] = None
    """直接经济损失  单位：亿元"""
    direct_economic_loss: Optional[float] = None
    """受淹城镇"""
    flooded_towns: Optional[int] = None
    """主键ID"""
    id: Optional[int] = None
    """逻辑删除标记"""
    is_deleted: Optional[int] = None
    """因灾失踪人口"""
    missing: Optional[int] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区名称"""
    region_name: Optional[str] = None
    """转移人口"""
    relocated: Optional[int] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None
    """水利工程设施直接经济损失  单位：亿元"""
    water_conservancy_loss: Optional[float] = None


@dataclass
class DaWaterEngineeringDamageRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.dawaterengineeringdamage.vo.DaWaterEngineeringDamageRespVO
    
    DaWaterEngineeringDamageRespVO
    """
    """堤防决口（1级堤防）处数"""
    breach_levee1_st_count: Optional[int] = None
    """堤防决口（1级堤防）长度"""
    breach_levee1_st_length: Optional[float] = None
    """堤防决口（1级堤防）损失"""
    breach_levee1_st_loss: Optional[float] = None
    """堤防决口（2级堤防）处数"""
    breach_levee2_nd_count: Optional[int] = None
    """堤防决口（2级堤防）长度"""
    breach_levee2_nd_length: Optional[float] = None
    """堤防决口（2级堤防）损失"""
    breach_levee2_nd_loss: Optional[float] = None
    """堤防决口（3级及以下堤防）处数"""
    breach_levee3_rd_count: Optional[int] = None
    """堤防决口（3级及以下堤防）长度"""
    breach_levee3_rd_length: Optional[float] = None
    """堤防决口（3级及以下堤防）损失"""
    breach_levee3_rd_loss: Optional[float] = None
    """水库垮坝（大(1)型）数量"""
    breach_reservoir_large1_count: Optional[int] = None
    """水库垮坝（大(1)型）损失"""
    breach_reservoir_large1_loss: Optional[float] = None
    """水库垮坝（大(2)型）数量"""
    breach_reservoir_large2_count: Optional[int] = None
    """水库垮坝（大(2)型）损失"""
    breach_reservoir_large2_loss: Optional[float] = None
    """水库垮坝（中型）数量"""
    breach_reservoir_medium_count: Optional[int] = None
    """水库垮坝（中型）损失"""
    breach_reservoir_medium_loss: Optional[float] = None
    """水库垮坝（小(1)型）数量"""
    breach_reservoir_small1_count: Optional[int] = None
    """水库垮坝（小(1)型）损失"""
    breach_reservoir_small1_loss: Optional[float] = None
    """水库垮坝（小(2)型）数量"""
    breach_reservoir_small2_count: Optional[int] = None
    """水库垮坝（小(2)型）损失"""
    breach_reservoir_small2_loss: Optional[float] = None
    """损坏水电站（大中型）数量"""
    damaged_hydro_large_medium_count: Optional[int] = None
    """损坏水电站（大中型）损失"""
    damaged_hydro_large_medium_loss: Optional[float] = None
    """损坏水文测站数量"""
    damaged_hydrometric_stations_count: Optional[int] = None
    """损坏水文测站损失"""
    damaged_hydrometric_stations_loss: Optional[float] = None
    """损坏水电站（小型）数量"""
    damaged_hydro_small_count: Optional[int] = None
    """损坏水电站（小型）损失"""
    damaged_hydro_small_loss: Optional[float] = None
    """损坏堤防（1级堤防）处数"""
    damaged_levee1_st_count: Optional[int] = None
    """损坏堤防（1级堤防）长度"""
    damaged_levee1_st_length: Optional[float] = None
    """损坏堤防（1级堤防）损失"""
    damaged_levee1_st_loss: Optional[float] = None
    """损坏堤防（2级堤防）处数"""
    damaged_levee2_nd_count: Optional[int] = None
    """损坏堤防（2级堤防）长度"""
    damaged_levee2_nd_length: Optional[float] = None
    """损坏堤防（2级堤防）损失"""
    damaged_levee2_nd_loss: Optional[float] = None
    """损坏堤防（3级及以下堤防）处数"""
    damaged_levee3_rd_count: Optional[int] = None
    """损坏堤防（3级及以下堤防）长度"""
    damaged_levee3_rd_length: Optional[float] = None
    """损坏堤防（3级及以下堤防）损失"""
    damaged_levee3_rd_loss: Optional[float] = None
    """损坏机电泵站数量"""
    damaged_pump_station_count: Optional[int] = None
    """损坏机电泵站损失"""
    damaged_pump_station_loss: Optional[float] = None
    """损坏水库（大(1)型）数量"""
    damaged_reservoir_large1_count: Optional[int] = None
    """损坏水库（大(1)型）损失"""
    damaged_reservoir_large1_loss: Optional[float] = None
    """损坏水库（大(2)型）数量"""
    damaged_reservoir_large2_count: Optional[int] = None
    """损坏水库（大(2)型）损失"""
    damaged_reservoir_large2_loss: Optional[float] = None
    """损坏水库（中型）数量"""
    damaged_reservoir_medium_count: Optional[int] = None
    """损坏水库（中型）损失"""
    damaged_reservoir_medium_loss: Optional[float] = None
    """损坏水库（小(1)型）数量"""
    damaged_reservoir_small1_count: Optional[int] = None
    """损坏水库（小(1)型）损失"""
    damaged_reservoir_small1_loss: Optional[float] = None
    """损坏水库（小(2)型）数量"""
    damaged_reservoir_small2_count: Optional[int] = None
    """损坏水库（小(2)型）损失"""
    damaged_reservoir_small2_loss: Optional[float] = None
    """损坏机电井数量"""
    damaged_well_count: Optional[int] = None
    """损坏机电井损失"""
    damaged_well_loss: Optional[float] = None
    """水利工程设施直接经济损失"""
    direct_economic_loss: Optional[float] = None
    """主键ID"""
    id: Optional[int] = None
    """逻辑删除标记"""
    is_deleted: Optional[int] = None
    """其他损坏数量"""
    other_damage_count: Optional[int] = None
    """其他损坏损失"""
    other_damage_loss: Optional[float] = None
    """地区ID"""
    region_id: Optional[int] = None
    """行政级别"""
    region_level: Optional[str] = None
    """地区名称"""
    region_name: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None


@dataclass
class DaFloodResponseTechSupportRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.dafloodresponsetechsupport.vo.DaFloodResponseTechSupportRespVO
    
    DaFloodResponseTechSupportRespVO
    """
    """防洪减灾效益 - 避免县级以上城镇受淹"""
    benefit_avoid_flood_city: Optional[int] = None
    """防洪减灾效益 - 防洪减灾经济效益"""
    benefit_economic: Optional[float] = None
    """防洪减灾效益 - 减淹耕地"""
    benefit_reduced_cropland: Optional[float] = None
    """防洪减灾效益 - 减少受灾人口"""
    benefit_reduced_population: Optional[float] = None
    """专家（工作组）- 市级"""
    expert_group_city: Optional[int] = None
    """专家（工作组）- 县（区）级"""
    expert_group_county: Optional[int] = None
    """专家（工作组）- 省级"""
    expert_group_province: Optional[int] = None
    """专家（工作组）- 合计"""
    expert_group_total: Optional[int] = None
    """技术支撑投入"""
    fund_input_tech: Optional[float] = None
    """省级及以下资金投入 - 总计"""
    fund_input_total: Optional[float] = None
    """水利救灾资金投入"""
    fund_input_water_res: Optional[float] = None
    """主键ID"""
    id: Optional[int] = None
    """巡堤查险（人天）"""
    patrol_man_days: Optional[int] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区"""
    region_name: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None


@dataclass
class DaLeveeBreachRecordRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.daleveebreachrecord.vo.DaLeveeBreachRecordRespVO
    
    DaLeveeBreachRecordRespVO
    """
    """受灾人口"""
    affected_population: Optional[int] = None
    """决口原因"""
    breach_cause: Optional[str] = None
    """决口形式"""
    breach_form: Optional[str] = None
    """决口位置"""
    breach_location: Optional[str] = None
    """决口时间"""
    breach_time: Optional[str] = None
    """决口宽度"""
    breach_width: Optional[float] = None
    """主键ID"""
    id: Optional[int] = None
    """堤防级别"""
    levee_level: Optional[str] = None
    """堤防名称"""
    levee_name: Optional[str] = None
    """管理单位"""
    management_unit: Optional[str] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区"""
    region_name: Optional[str] = None
    """备注"""
    remarks: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None
    """起始桩号"""
    starting_stake_number: Optional[str] = None
    """所在水系"""
    water_system: Optional[str] = None


@dataclass
class DaMajorWaterDamageRecordRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.damajorwaterdamagerecord.vo.DaMajorWaterDamageRecordRespVO
    
    DaMajorWaterDamageRecordRespVO
    """
    """损毁原因"""
    damage_cause: Optional[str] = None
    """损毁描述"""
    damage_description: Optional[str] = None
    """水毁等级"""
    damage_grade: Optional[str] = None
    """水毁损失"""
    damage_loss: Optional[float] = None
    """主键ID"""
    id: Optional[int] = None
    """所在位置"""
    location: Optional[str] = None
    """管理单位"""
    management_unit: Optional[str] = None
    """工程级别"""
    project_level: Optional[str] = None
    """工程名称"""
    project_name: Optional[str] = None
    """工程类型"""
    project_type: Optional[str] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区"""
    region_name: Optional[str] = None
    """备注"""
    remarks: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None


@dataclass
class DaMountainFloodDefenseRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.damountainflooddefense.vo.DaMountainFloodDefenseRespVO
    
    DaMountainFloodDefenseRespVO
    """
    """启动预警广播"""
    alert_broadcast_times: Optional[int] = None
    """预警发布服务人数"""
    alert_service_population: Optional[float] = None
    """发布预警的县数"""
    county_alert_count: Optional[int] = None
    """转移人数"""
    evacuated_population: Optional[float] = None
    """主键ID"""
    id: Optional[int] = None
    """发布山洪灾害的次数"""
    mudflood_alert_times: Optional[int] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区"""
    region_name: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None
    """向社会公众发布预警短信条数"""
    sms_to_public: Optional[float] = None
    """向责任人发布预警短信条数"""
    sms_to_responsible_person: Optional[float] = None
    """发布预警次数（总）"""
    total_alert_times: Optional[int] = None


@dataclass
class DaMountainFloodEventRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.damountainfloodevent.vo.DaMountainFloodEventRespVO
    
    DaMountainFloodEventRespVO
    """
    """受灾人口"""
    affected_population: Optional[float] = None
    """倒塌房屋"""
    collapsed_homes: Optional[int] = None
    """死亡人数"""
    death_count: Optional[int] = None
    """灾害类型"""
    disaster_type: Optional[str] = None
    """经济损失"""
    economic_loss: Optional[float] = None
    """主键ID"""
    id: Optional[int] = None
    """是否发布预警"""
    is_alert_issued: Optional[str] = None
    """发生地点 -县（市、区）-乡（镇、街道）-村（社区）"""
    location_county: Optional[str] = None
    """实测最大降雨量 - 1小时"""
    max_rainfall1_h: Optional[float] = None
    """实测最大降雨量 - 24小时"""
    max_rainfall24_h: Optional[float] = None
    """实测最大降雨量 - 3小时"""
    max_rainfall3_h: Optional[float] = None
    """实测最大降雨量 - 6小时"""
    max_rainfall6_h: Optional[float] = None
    """失踪人数"""
    missing_count: Optional[int] = None
    """发生时间"""
    occurred_time: Optional[str] = None
    """地区"""
    region_name: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None


@dataclass
class DaReservoirBreachRecordRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.dareservoirbreachrecord.vo.DaReservoirBreachRecordRespVO
    
    DaReservoirBreachRecordRespVO
    """
    """受灾人口"""
    affected_population: Optional[int] = None
    """垮坝原因"""
    breach_cause: Optional[str] = None
    """垮坝形式"""
    breach_form: Optional[str] = None
    """垮坝位置"""
    breach_location: Optional[str] = None
    """垮坝时间"""
    breach_time: Optional[str] = None
    """坝高"""
    dam_height: Optional[float] = None
    """大坝类型"""
    dam_type: Optional[str] = None
    """主键ID"""
    id: Optional[int] = None
    """管理单位"""
    management_unit: Optional[str] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区"""
    region_name: Optional[str] = None
    """备注"""
    remarks: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None
    """水库名称"""
    reservoir_name: Optional[str] = None
    """水库规模"""
    reservoir_scale: Optional[str] = None
    """总库容"""
    total_capacity: Optional[float] = None
    """水库所在水系"""
    water_system: Optional[str] = None


@dataclass
class DaUrbanFloodStatisticsRespVO:
    """
    com.yulin.fad.module.shzh.controller.admin.disaster.daurbanfloodstatistics.vo.DaUrbanFloodStatisticsRespVO
    
    DaUrbanFloodStatisticsRespVO
    """
    """城镇名称"""
    city_name: Optional[str] = None
    """淹没历时"""
    flood_duration: Optional[float] = None
    """受淹面积"""
    flooded_area: Optional[float] = None
    """受淹面积比例"""
    flooded_area_ratio: Optional[float] = None
    """主键ID"""
    id: Optional[int] = None
    """进水时间"""
    inundation_time: Optional[str] = None
    """主要街区最大水深"""
    max_water_depth: Optional[float] = None
    """地区ID"""
    region_id: Optional[int] = None
    """地区"""
    region_name: Optional[str] = None
    """报表实例ID"""
    report_instance_id: Optional[int] = None
    """进水时代表站水位"""
    water_level: Optional[float] = None


@dataclass
class DaDisasterReportInstanceRespVO:
    """返回数据
    
    DaDisasterReportInstanceRespVO
    """
    """农业灾情及抗旱情况统计数据"""
    agri_disaster_drought_resist_list: Optional[List[DaAgriDisasterDroughtResistRespVO]] = None
    """农业旱情动态情况数据"""
    agri_drought_dynamic_list: Optional[List[DaAgriDroughtDynamicRespVO]] = None
    """农业旱情及抗旱情况统计数据"""
    agri_drought_resist_list: Optional[List[DaAgriDroughtResistRespVO]] = None
    """农业抗旱情况统计数据"""
    agri_drought_resist_only_list: Optional[List[DaAgriDroughtResistOnlyRespVO]] = None
    """创建时间"""
    create_time: Optional[str] = None
    """模板信息"""
    da_disaster_report_template_resp_vo: Optional[DaDisasterReportTemplateRespVO] = None
    """洪涝灾害基本统计数据"""
    da_flood_disaster_statistics_info: Optional[List[DaFloodDisasterStatisticsInfoRespVO]] = None
    """水利工程设施洪涝灾害统计数据"""
    da_water_engineering_damage_list: Optional[List[DaWaterEngineeringDamageRespVO]] = None
    """灾害类型  0=洪涝灾害，1=旱灾，2=山洪灾害"""
    disaster_type: Optional[str] = None
    """截止日期"""
    end_date: Optional[str] = None
    """抗洪抢险技术支撑情况统计数据"""
    flood_response_tech_support_list: Optional[List[DaFloodResponseTechSupportRespVO]] = None
    """填表人ID"""
    form_filler_id: Optional[str] = None
    """填表人姓名"""
    form_filler_name: Optional[str] = None
    """主键ID"""
    id: Optional[int] = None
    """逻辑删除标记"""
    is_deleted: Optional[int] = None
    """堤防决口数据"""
    levee_breach_record_list: Optional[List[DaLeveeBreachRecordRespVO]] = None
    """较大重大水毁工程台账数据"""
    major_water_damage_record_list: Optional[List[DaMajorWaterDamageRecordRespVO]] = None
    """山洪灾害防御情况统计数据"""
    mountain_flood_defense_list: Optional[List[DaMountainFloodDefenseRespVO]] = None
    """山洪灾害事件统计数据"""
    mountain_flood_event_list: Optional[List[DaMountainFloodEventRespVO]] = None
    """填报单位ID"""
    reporting_unit_id: Optional[str] = None
    """填报单位名称"""
    reporting_unit_name: Optional[str] = None
    """报告期别"""
    report_period: Optional[str] = None
    """水库垮坝数据"""
    reservoir_breach_record_list: Optional[List[DaReservoirBreachRecordRespVO]] = None
    """起始日期"""
    start_date: Optional[str] = None
    """统计负责人ID"""
    statistics_manager_id: Optional[str] = None
    """统计负责人姓名"""
    statistics_manager_name: Optional[str] = None
    """状态  0=草稿，1=已提交，2=已审核，3=已驳回"""
    status: Optional[str] = None
    """报出日期"""
    submission_date: Optional[str] = None
    """关联的报表模板ID"""
    template_id: Optional[int] = None
    """模板名称"""
    template_name: Optional[str] = None
    """单位负责人ID"""
    unit_head_id: Optional[str] = None
    """单位负责人姓名"""
    unit_head_name: Optional[str] = None
    """城镇受淹情况统计数据"""
    urban_flood_statistics_list: Optional[List[DaUrbanFloodStatisticsRespVO]] = None


@dataclass
class ApifoxModel:
    """CommonResultDaDisasterReportInstanceRespVO"""
    """错误码"""
    code: Optional[int] = None
    """返回数据"""
    data: Optional[DaDisasterReportInstanceRespVO] = None
    """错误提示，用户可阅读"""
    msg: Optional[str] = None