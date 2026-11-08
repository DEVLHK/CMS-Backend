-- MySQL dump 10.13  Distrib 9.7.1, for macos26.4 (arm64)
--
-- Host: 192.168.201.89    Database: oms
-- ------------------------------------------------------
-- Server version	9.1.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `oms`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `oms` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `oms`;

--
-- Table structure for table `common_selection`
--

DROP TABLE IF EXISTS `common_selection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `common_selection` (
  `project_id` varchar(32) NOT NULL,
  `type` varchar(32) NOT NULL,
  `code` varchar(32) NOT NULL,
  `cn_description` varchar(255) DEFAULT NULL COMMENT '中⽂',
  `en_description` varchar(255) DEFAULT NULL COMMENT '英⽂',
  `sub_type` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`project_id`,`type`,`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='下拉选项表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deployment_approval_comment_info`
--

DROP TABLE IF EXISTS `deployment_approval_comment_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deployment_approval_comment_info` (
  `approval_id` varchar(32) NOT NULL,
  `approval_id_index` int NOT NULL,
  `remark` varchar(255) DEFAULT NULL,
  `comment_user` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`approval_id`,`approval_id_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='版本审批备注历史表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deployment_approval_info`
--

DROP TABLE IF EXISTS `deployment_approval_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deployment_approval_info` (
  `approval_id` varchar(32) NOT NULL,
  `project_id` varchar(32) DEFAULT NULL,
  `deploy_id` varchar(10) DEFAULT NULL,
  `workflow_id` varchar(32) DEFAULT NULL,
  `workflow_step` char(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `approved_user_list` varchar(255) DEFAULT NULL,
  `approval_status` char(1) DEFAULT NULL,
  PRIMARY KEY (`approval_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='版本审批历史表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deployment_resource_detail`
--

DROP TABLE IF EXISTS `deployment_resource_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deployment_resource_detail` (
  `resource_id` char(32) NOT NULL,
  `resource_id_index` int NOT NULL,
  `record_index` int NOT NULL COMMENT '按resourceid和resource_id_index加1',
  `project_id` char(32) DEFAULT NULL,
  `resource_name` varchar(600) DEFAULT NULL,
  `gitlab_ref_name` char(32) DEFAULT NULL COMMENT '针对cobol核⼼，⽤于执⾏时与审批时的对⽐',
  `git_project_name` char(32) DEFAULT NULL,
  `from_tag` char(32) DEFAULT NULL COMMENT '针对⾮核⼼系统，',
  `deploy_tag` char(32) DEFAULT NULL COMMENT '针对⾮核⼼系统部分',
  `resource_file_list` varchar(255) DEFAULT NULL COMMENT '⽂件名称列表,⽤于有上传⽂件的场景',
  `resource_path` varchar(255) DEFAULT NULL COMMENT '⽂件上传后在服务器的路径',
  `operation_remark` text,
  `remark` varchar(600) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `sql_statement` text,
  `from_server_id` char(32) DEFAULT NULL,
  `service_protocol` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `service_start_port` int DEFAULT NULL,
  `service_end_port` int DEFAULT NULL,
  `service_server_id` char(32) DEFAULT NULL,
  PRIMARY KEY (`resource_id`,`resource_id_index`,`record_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='版本发布资源详细信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deployment_resource_type`
--

DROP TABLE IF EXISTS `deployment_resource_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deployment_resource_type` (
  `resource_id` varchar(32) NOT NULL COMMENT '格式 RES-YYMMDD-999, 999为当天顺序号',
  `resource_id_index` int NOT NULL COMMENT '按resource_id加1',
  `project_id` varchar(32) DEFAULT NULL,
  `system_type` char(32) DEFAULT NULL COMMENT '1-cobol核⼼\r\n2-电⼦银⾏\r\n3-外围\r\n4-LOS',
  `system_sub_type` char(32) DEFAULT NULL COMMENT '1.1-cobol核⼼后台\r\n1.2-branch2.0\r\n2.1-后管前端\r\n2.2-⽹银前端\r\n2.3-⼿机App\r\n2.4-电⼦银⾏后台\r\n3.1-前端\r\n3.2-后台',
  `resource_type` varchar(32) DEFAULT NULL COMMENT '1-代码\r\n2-服务器配置⽂件\r\n3-Nacos配置\r\n4-数据\r\n5-数据结构\r\n6-⽹络策略\r\n7-脚本\r\n8-调度图\r\n9-其它',
  `deploy_server_list` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '申请发布的服务器清单',
  `remark` varchar(600) DEFAULT NULL,
  `status` char(1) DEFAULT NULL COMMENT '1-Checked',
  PRIMARY KEY (`resource_id`,`resource_id_index`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='版本发布资源类型表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deployment_status`
--

DROP TABLE IF EXISTS `deployment_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deployment_status` (
  `deploy_id` varchar(64) NOT NULL COMMENT '随机⽣成,全局唯⼀',
  `project_id` varchar(20) DEFAULT NULL,
  `issue_id` varchar(10) DEFAULT NULL COMMENT '格式：PMSXXXX或者是需求编号',
  `user_id` varchar(64) DEFAULT NULL,
  `apply_for_env` varchar(32) DEFAULT NULL,
  `current_deployed_env` varchar(32) DEFAULT NULL COMMENT '只有当发布到下⼀个环境的时候才填写',
  `status` varchar(2) DEFAULT NULL COMMENT '1-草稿\r\n2-已提交，待审批\r\n3-已提交，待其他⼈发起审批\r\n4-审批通过，待发布\r\n5-审批拒绝\r\n6-发布中\r\n7-已发布当前环境\r\n8-已发布后续环境\r\n9-完成\r\n10-取消',
  `author_list` varchar(255) DEFAULT NULL,
  `parent_deploy_id_list` varchar(255) DEFAULT NULL COMMENT '记录从哪些deploy_id发布⽽来，需要结合userid来统计',
  `next_deploy_id` varchar(255) DEFAULT NULL COMMENT '记录发布到⼀下节点时，创建的deploy_id',
  `current_approval_queue` char(2) DEFAULT NULL COMMENT '01-⼀⼿审批\r\n02-⼆⼿审批\r\n03-三⼿审批\r\nxx-xx⼿审批\r\n99-拒绝队列\r\n00-未在审批队列\r\n98-最后⼀⼿审批',
  `resource_id` varchar(32) DEFAULT NULL,
  `deploy_in_order` int DEFAULT NULL,
  `deploy_in_order_flg` char(1) DEFAULT NULL COMMENT 'Y-有顺序要求\r\n N-⽆没有顺序要求',
  `suspicious_event_id` varchar(64) DEFAULT NULL,
  `create_user` varchar(64) DEFAULT NULL,
  `last_deploy_date` date DEFAULT NULL,
  `last_deploy_time` time DEFAULT NULL,
  `create_date` date DEFAULT NULL,
  `create_time` time DEFAULT NULL,
  `last_update_user` varchar(64) DEFAULT NULL,
  `last_update_date` date DEFAULT NULL,
  `last_update_time` time DEFAULT NULL,
  `ts` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  `risk_level` char(1) DEFAULT NULL,
  `suspicious_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`deploy_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='版本发布状态表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deployment_suspicious_detail`
--

DROP TABLE IF EXISTS `deployment_suspicious_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deployment_suspicious_detail` (
  `suspicious_id` varchar(64) NOT NULL COMMENT 'YES	SUSP-YYMMDDHHmmss-99，全局唯一,99是两位随机数',
  `suspicious_id_index` int NOT NULL,
  `index` int NOT NULL,
  `project_id` varchar(32) DEFAULT NULL,
  `resource_id` varchar(64) DEFAULT NULL,
  `resource_id_index` int DEFAULT NULL,
  `suspicious_resource_name` varchar(64) DEFAULT NULL,
  `conflict_deploy_id` varchar(64) DEFAULT NULL,
  `related_user` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `related_deploy_id` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`suspicious_id`,`suspicious_id_index`,`index`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deployment_suspicious_type`
--

DROP TABLE IF EXISTS `deployment_suspicious_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deployment_suspicious_type` (
  `suspicious_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'SUSP-YYMMDDHHmmss-99，全局唯⼀,99是两位随机数',
  `suspicious_id_index` int NOT NULL,
  `project_id` varchar(32) DEFAULT NULL,
  `suspicious_type` char(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '1-cobol核⼼同⼀个PMS更新了多个代码，但只要求上部分资源\r\n2-当前版本与其它版本有资源冲突\r\n3-资源类型为其它\r\n4-版本被多次提版\r\n5-有多⼈同时提版\r\n6-有数据更新\r\n7-有数据结构更新\r\n8-有jar依赖包更新\r\n9-有新版本在发布于更早的节点\r\n10-资源没有发布到节点下所有服务器',
  `risk_level` char(1) DEFAULT NULL COMMENT '1-低\r\n2-中\r\n3-⾼',
  `resource_id` varchar(64) DEFAULT NULL,
  `resource_id_index` int DEFAULT NULL,
  `suspicious_resource_name` varchar(255) DEFAULT NULL,
  `suspicious_resource_detail` varchar(255) DEFAULT NULL,
  `conflict_deploy_id` varchar(255) DEFAULT NULL,
  `conflict_strategy_type` char(1) DEFAULT NULL COMMENT '1-必须同时发版\r\n2-按顺序发版本\r\n针对suspicious_type=2',
  `conflict_deploy_order` varchar(255) DEFAULT NULL COMMENT 'deploy_id1,deploy_id2,deploy_id3,deploy_id4,......',
  `related_user_id_list` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`suspicious_id`,`suspicious_id_index`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='版本可疑事项登记表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deployment_transaction_config`
--

DROP TABLE IF EXISTS `deployment_transaction_config`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deployment_transaction_config` (
  `project_id` char(32) NOT NULL,
  `system_type` char(32) NOT NULL,
  `system_sub_type` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `resource_type` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `transaction_type` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`project_id`,`system_type`,`system_sub_type`,`resource_type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='资源配置表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `deployment_workflow`
--

DROP TABLE IF EXISTS `deployment_workflow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `deployment_workflow` (
  `project_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `env_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `step` int NOT NULL,
  `approval_role_list` text,
  `approval_number` int DEFAULT NULL,
  PRIMARY KEY (`project_id`,`env_id`,`step`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='⼯作流表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `etl_other_blob`
--

DROP TABLE IF EXISTS `etl_other_blob`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etl_other_blob` (
  `project_id` char(20) NOT NULL,
  `table_name` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `table_blob_field_name` char(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `copybook_name` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `copybook_blob_field_name` char(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`project_id`,`table_name`,`table_blob_field_name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `etl_parm_blob`
--

DROP TABLE IF EXISTS `etl_parm_blob`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etl_parm_blob` (
  `project_id` char(20) NOT NULL,
  `parm_type` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `copybook_name` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `copybook_parm_code_name` char(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `copybook_parm_value_name` char(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`project_id`,`parm_type`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `message_code_info`
--

DROP TABLE IF EXISTS `message_code_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `message_code_info` (
  `code` char(25) NOT NULL,
  `cn_message` varchar(255) DEFAULT NULL,
  `en_message` varchar(255) DEFAULT NULL,
  `type` char(1) DEFAULT NULL COMMENT 'E-错误\nW-警告',
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mock_cbs_service`
--

DROP TABLE IF EXISTS `mock_cbs_service`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mock_cbs_service` (
  `project_id` varchar(20) NOT NULL,
  `code` varchar(20) NOT NULL,
  `method` char(1) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL COMMENT 'I:Internal API\nE:External API',
  `name` varchar(120) NOT NULL,
  `en_name` varchar(250) DEFAULT NULL,
  `type` char(1) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `is_issue` tinyint(1) NOT NULL,
  `fmt_out` tinyint(1) NOT NULL,
  `fmt` varchar(100) DEFAULT NULL,
  `file_out` tinyint(1) NOT NULL,
  `list_out` tinyint(1) NOT NULL DEFAULT '0',
  `auto_filter` tinyint(1) NOT NULL DEFAULT '0',
  `version` varchar(10) DEFAULT NULL,
  `remark` varchar(255) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `en_remark` varchar(600) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL,
  `bck_id` int NOT NULL DEFAULT '0',
  `interface` mediumtext,
  PRIMARY KEY (`project_id`,`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `mock_interface`
--

DROP TABLE IF EXISTS `mock_interface`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mock_interface` (
  `project_id` varchar(20) NOT NULL,
  `code` varchar(20) NOT NULL,
  `interface` mediumtext,
  PRIMARY KEY (`project_id`,`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pms_bug_daily_detail`
--

DROP TABLE IF EXISTS `pms_bug_daily_detail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pms_bug_daily_detail` (
  `record_date` date NOT NULL,
  `id` mediumint NOT NULL DEFAULT '0',
  `project` mediumint unsigned NOT NULL DEFAULT '0',
  `product` mediumint unsigned NOT NULL DEFAULT '0',
  `injection` mediumint unsigned NOT NULL DEFAULT '0',
  `identify` mediumint unsigned NOT NULL DEFAULT '0',
  `branch` mediumint unsigned NOT NULL DEFAULT '0',
  `module` mediumint unsigned NOT NULL DEFAULT '0',
  `execution` mediumint unsigned NOT NULL DEFAULT '0',
  `plan` mediumint unsigned NOT NULL DEFAULT '0',
  `story` mediumint unsigned NOT NULL DEFAULT '0',
  `storyVersion` smallint NOT NULL DEFAULT '1',
  `task` mediumint unsigned NOT NULL DEFAULT '0',
  `toTask` mediumint unsigned NOT NULL DEFAULT '0',
  `toStory` mediumint NOT NULL DEFAULT '0',
  `title` varchar(255) NOT NULL DEFAULT '',
  `keywords` varchar(255) NOT NULL DEFAULT '',
  `severity` tinyint NOT NULL DEFAULT '0',
  `pri` tinyint unsigned NOT NULL DEFAULT '0',
  `type` varchar(30) NOT NULL DEFAULT '',
  `status` varchar(32) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT 'new',
  `due_today` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `due_tomorrow` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `due_in_2_days` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `pending_for_test_today` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `pending_for_test_2_days` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `close_today` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `retest_today` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `create_today` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `new_status_1_days` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `test_failed_today` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `test_failed_1_days` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `resolved_today` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `no_deadline` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `overdue` varchar(5) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `overdue_days` varchar(10) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci NOT NULL DEFAULT '',
  `confirmed` tinyint(1) NOT NULL DEFAULT '0',
  `activatedCount` smallint NOT NULL DEFAULT '0',
  `reopenCount` smallint NOT NULL DEFAULT '0',
  `activatedDate` datetime DEFAULT NULL,
  `mailto` text,
  `openedBy` varchar(30) NOT NULL DEFAULT '',
  `openedDate` datetime DEFAULT NULL,
  `openedBuild` varchar(255) NOT NULL DEFAULT '',
  `assignedTo` varchar(30) NOT NULL DEFAULT '',
  `assignedDate` datetime DEFAULT NULL,
  `deadline` date DEFAULT NULL,
  `resolvedBy` varchar(30) NOT NULL DEFAULT '',
  `resolution` varchar(30) NOT NULL DEFAULT '',
  `resolvedBuild` varchar(30) NOT NULL DEFAULT '',
  `resolvedDate` datetime DEFAULT NULL,
  `closedBy` varchar(30) NOT NULL DEFAULT '',
  `closedDate` datetime DEFAULT NULL,
  `duplicateBug` mediumint unsigned NOT NULL DEFAULT '0',
  `relatedBug` varchar(255) NOT NULL DEFAULT '',
  `case` mediumint unsigned NOT NULL DEFAULT '0',
  `testtask` mediumint unsigned NOT NULL DEFAULT '0',
  `lastEditedBy` varchar(30) NOT NULL DEFAULT '',
  `lastEditedDate` datetime DEFAULT NULL,
  `deleted` enum('0','1') NOT NULL DEFAULT '0',
  `category` varchar(10) NOT NULL DEFAULT '1' COMMENT 'bug类别',
  `stage` mediumint NOT NULL DEFAULT '1' COMMENT '需求阶段',
  PRIMARY KEY (`id`,`record_date`),
  KEY `product` (`product`),
  KEY `execution` (`execution`),
  KEY `status` (`status`),
  KEY `plan` (`plan`),
  KEY `story` (`story`),
  KEY `case` (`case`),
  KEY `toStory` (`toStory`),
  KEY `assignedTo` (`assignedTo`),
  KEY `deleted` (`deleted`),
  KEY `product_status_deleted` (`product`,`status`,`deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pms_bug_daily_status`
--

DROP TABLE IF EXISTS `pms_bug_daily_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pms_bug_daily_status` (
  `date` date NOT NULL,
  `project_id` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `execution_id` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `module` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `owner` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `status` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `team` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `group` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `status_count` int NOT NULL,
  PRIMARY KEY (`date`,`project_id`,`execution_id`,`module`,`owner`,`status`,`team`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pms_failed_bug`
--

DROP TABLE IF EXISTS `pms_failed_bug`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pms_failed_bug` (
  `bug_id` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '缺陷编号（如 BUG-2026-0001）',
  `project_id` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '项目编号（搜索条件）',
  `bug_title` varchar(200) COLLATE utf8mb4_general_ci NOT NULL COMMENT '缺陷标题',
  `last_test_fail_date` date NOT NULL COMMENT '最近一次复测失败日期',
  `bug_status` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '缺陷当前状态（字符串，原样存储与返回，默认空字符串）',
  `bug_create_time` datetime NOT NULL COMMENT '缺陷创建时间',
  `last_resolver` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '缺陷最后解决人',
  `last_qa_owner` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '缺陷最后QA人员',
  `review_status` tinyint NOT NULL DEFAULT '2' COMMENT '审阅状态 1:已审阅 2:未审阅',
  `last_review_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '最后审阅人（登录账号）',
  `last_review_time` datetime DEFAULT NULL COMMENT '最后审阅时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_id`,`bug_id`),
  KEY `idx_review_status` (`review_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='失败缺陷表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pms_failed_bug_comment`
--

DROP TABLE IF EXISTS `pms_failed_bug_comment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pms_failed_bug_comment` (
  `project_id` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '项目编号',
  `bug_id` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '缺陷编号（如 BUG-2026-0001）',
  `seq_no` int unsigned NOT NULL COMMENT '点评序号，同 project_id+bug_id 内从 1 递增（后端生成）',
  `test_failure_date` date NOT NULL COMMENT '该次点评对应的复测失败日期',
  `action_id` varchar(10) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '来源动作ID（zt_action.id，同步脚本写入，API 暂不维护）',
  `last_resolver` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '缺陷最后解决人（点评时快照）',
  `qa_owner` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '缺陷QA人员（点评时快照）',
  `failure_reason_category` tinyint DEFAULT NULL COMMENT '失败原因分类（字典 1-11，空=待点评，同步占位）',
  `failure_reason` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '失败原因描述',
  `is_caused_by_fixing` tinyint NOT NULL DEFAULT '0' COMMENT '是否因修复其他缺陷引入 1:是 0:否',
  `suggestion` varchar(1000) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '改进建议',
  `comment_date` datetime DEFAULT NULL COMMENT '点评时间（新增时后端取当前时间）',
  `commented_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '点评人（登录账号，新增时取 token）',
  `reviewer` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '审阅人（登录账号）',
  `review_date` datetime DEFAULT NULL COMMENT '审阅时间',
  `review_status` tinyint NOT NULL DEFAULT '2' COMMENT '审阅状态 1:已审阅 2:未审阅',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`project_id`,`bug_id`,`seq_no`),
  KEY `idx_test_failure_date` (`test_failure_date`),
  KEY `idx_review_status` (`review_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='失败缺陷点评表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pms_report_uat_summary`
--

DROP TABLE IF EXISTS `pms_report_uat_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pms_report_uat_summary` (
  `date` date NOT NULL,
  `project_id` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `execution_id` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `module` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `team` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `group` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `cycle_time` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `aging_index` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `daily_fix_rate` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `test_execution_rate` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `test_failure_rate` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `reopen_rate` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `bug_closure_rate` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`date`,`project_id`,`execution_id`,`module`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pms_task_analytical_status`
--

DROP TABLE IF EXISTS `pms_task_analytical_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pms_task_analytical_status` (
  `id` mediumint unsigned NOT NULL AUTO_INCREMENT,
  `project` mediumint unsigned NOT NULL DEFAULT '0',
  `parent` mediumint NOT NULL DEFAULT '0',
  `isParent` tinyint(1) NOT NULL DEFAULT '0',
  `path` text,
  `group` varchar(255) NOT NULL DEFAULT '',
  `team` varchar(255) NOT NULL DEFAULT '',
  `execution` mediumint unsigned NOT NULL DEFAULT '0',
  `module` mediumint unsigned NOT NULL DEFAULT '0',
  `design` mediumint unsigned NOT NULL DEFAULT '0',
  `story` mediumint unsigned NOT NULL DEFAULT '0',
  `storyVersion` smallint NOT NULL DEFAULT '1',
  `designVersion` smallint unsigned NOT NULL DEFAULT '1',
  `fromBug` mediumint unsigned NOT NULL DEFAULT '0',
  `fromIssue` mediumint unsigned NOT NULL DEFAULT '0',
  `feedback` mediumint unsigned NOT NULL DEFAULT '0',
  `name` varchar(255) NOT NULL DEFAULT '',
  `type` varchar(20) NOT NULL DEFAULT '',
  `mode` varchar(10) NOT NULL DEFAULT '',
  `pri` tinyint unsigned NOT NULL DEFAULT '0',
  `estimate` float unsigned NOT NULL DEFAULT '0',
  `consumed` float unsigned NOT NULL DEFAULT '0',
  `left` float unsigned NOT NULL DEFAULT '0',
  `deadline` date DEFAULT NULL,
  `overdue_days` int NOT NULL,
  `status` enum('wait','doing','done','pause','cancel','closed') NOT NULL DEFAULT 'wait',
  `subStatus` varchar(30) NOT NULL DEFAULT '',
  `color` char(7) NOT NULL DEFAULT '',
  `mailto` text,
  `keywords` varchar(255) NOT NULL DEFAULT '',
  `desc` mediumtext,
  `version` smallint NOT NULL DEFAULT '0',
  `openedBy` varchar(30) NOT NULL DEFAULT '',
  `openedDate` datetime DEFAULT NULL,
  `assignedTo` varchar(30) NOT NULL DEFAULT '',
  `assignedDate` datetime DEFAULT NULL,
  `estStarted` date DEFAULT NULL,
  `realStarted` datetime DEFAULT NULL,
  `finishedBy` varchar(30) NOT NULL DEFAULT '',
  `finishedDate` datetime DEFAULT NULL,
  `finishedList` text,
  `canceledBy` varchar(30) NOT NULL DEFAULT '',
  `canceledDate` datetime DEFAULT NULL,
  `closedBy` varchar(30) NOT NULL DEFAULT '',
  `closedDate` datetime DEFAULT NULL,
  `planDuration` int NOT NULL DEFAULT '0',
  `realDuration` int NOT NULL DEFAULT '0',
  `closedReason` varchar(30) NOT NULL DEFAULT '',
  `lastEditedBy` varchar(30) NOT NULL DEFAULT '',
  `lastEditedDate` datetime DEFAULT NULL,
  `activatedDate` datetime DEFAULT NULL,
  `order` mediumint unsigned NOT NULL DEFAULT '0',
  `repo` mediumint unsigned NOT NULL DEFAULT '0',
  `mr` mediumint unsigned NOT NULL DEFAULT '0',
  `entry` varchar(255) NOT NULL DEFAULT '',
  `lines` varchar(10) NOT NULL DEFAULT '',
  `v1` varchar(40) NOT NULL DEFAULT '',
  `v2` varchar(40) NOT NULL DEFAULT '',
  `deleted` enum('0','1') NOT NULL DEFAULT '0',
  `vision` varchar(10) NOT NULL DEFAULT 'rnd',
  `myIsAutoFromBug` char(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `execution` (`execution`),
  KEY `story` (`story`),
  KEY `parent` (`parent`),
  KEY `assignedTo` (`assignedTo`),
  KEY `order` (`order`)
) ENGINE=InnoDB AUTO_INCREMENT=40017 DEFAULT CHARSET=utf8mb3;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pms_task_daily_status`
--

DROP TABLE IF EXISTS `pms_task_daily_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pms_task_daily_status` (
  `date` date NOT NULL,
  `project_id` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `execution_id` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `module` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `owner` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `status` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `team_group` char(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `status_count` int NOT NULL,
  PRIMARY KEY (`date`,`project_id`,`execution_id`,`module`,`owner`,`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pms_team_group_list`
--

DROP TABLE IF EXISTS `pms_team_group_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pms_team_group_list` (
  `project_id` char(10) NOT NULL,
  `team_group_id` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `team_group_name` varchar(255) NOT NULL DEFAULT '',
  `pms_module_list` varchar(600) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`project_id`,`team_group_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pms_team_list`
--

DROP TABLE IF EXISTS `pms_team_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pms_team_list` (
  `project_id` char(10) NOT NULL,
  `team_id` char(60) NOT NULL,
  `team_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  `team_group_id` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '',
  PRIMARY KEY (`project_id`,`team_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `pms_team_member`
--

DROP TABLE IF EXISTS `pms_team_member`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pms_team_member` (
  `project_id` char(10) NOT NULL,
  `team_id` char(60) NOT NULL,
  `pms_user` char(120) NOT NULL,
  `allow_create_test_task` varchar(1) NOT NULL DEFAULT 'N',
  PRIMARY KEY (`project_id`,`team_id`,`pms_user`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_cbs_param`
--

DROP TABLE IF EXISTS `project_cbs_param`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_cbs_param` (
  `project_id` char(20) NOT NULL,
  `env_id` char(20) NOT NULL,
  `cbs_ip` char(25) NOT NULL,
  `cbs_port` char(10) NOT NULL,
  PRIMARY KEY (`project_id`,`env_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_db_param`
--

DROP TABLE IF EXISTS `project_db_param`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_db_param` (
  `project_id` char(20) NOT NULL,
  `database_type` char(10) NOT NULL,
  `database_host` char(20) NOT NULL,
  `database_port` char(10) NOT NULL,
  `database_name` char(25) NOT NULL,
  `database_client_dir` char(255) NOT NULL,
  `database_user` char(60) NOT NULL,
  `database_password` char(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`project_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_env_info`
--

DROP TABLE IF EXISTS `project_env_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_env_info` (
  `project_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `env_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `env_name` varchar(256) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`project_id`,`env_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='项⽬环境表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_gantt`
--

DROP TABLE IF EXISTS `project_gantt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_gantt` (
  `project_id` char(64) NOT NULL,
  `task_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `type` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT '',
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  PRIMARY KEY (`project_id`,`task_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_git_info`
--

DROP TABLE IF EXISTS `project_git_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_git_info` (
  `project_id` char(32) NOT NULL,
  `git_project_name` char(32) NOT NULL,
  `system_type` char(32) DEFAULT NULL,
  `system_sub_type` char(32) DEFAULT NULL,
  `access_token` char(32) DEFAULT NULL,
  `remark` varchar(600) DEFAULT NULL,
  PRIMARY KEY (`project_id`,`git_project_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='GIT⼯程信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_list`
--

DROP TABLE IF EXISTS `project_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_list` (
  `project_id` char(20) NOT NULL,
  `project_name` char(255) DEFAULT NULL,
  `service_ip` char(255) DEFAULT NULL,
  `enabled` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Y-Enable,N-Disable',
  PRIMARY KEY (`project_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_pms_param`
--

DROP TABLE IF EXISTS `project_pms_param`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_pms_param` (
  `project_id` char(20) NOT NULL,
  `pms_project_id` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `pms_url` char(255) NOT NULL,
  `pms_user` char(20) NOT NULL,
  `pms_password` char(60) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `pms_key` char(100) NOT NULL,
  `pms_code` char(20) NOT NULL,
  `notify_enable` char(1) NOT NULL,
  `notify_defect_url` char(255) NOT NULL,
  `notify_alert_weeks` char(15) NOT NULL,
  `notify_alert_day` char(2) NOT NULL,
  `notify_wecom_enable` char(1) NOT NULL,
  `notify_wecom_url` char(255) NOT NULL,
  `notify_email_enable` char(50) NOT NULL,
  `notify_email_host` char(50) NOT NULL,
  `notify_email_user` char(50) NOT NULL,
  `notify_email_password` char(30) NOT NULL,
  `notify_email_receiver` varchar(600) NOT NULL,
  `bank_user_prefix` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  PRIMARY KEY (`project_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_server_info`
--

DROP TABLE IF EXISTS `project_server_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_server_info` (
  `project_id` char(32) NOT NULL,
  `server_id` char(32) NOT NULL,
  `env_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `server_ip` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `server_name` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `remark` varchar(600) DEFAULT NULL,
  PRIMARY KEY (`project_id`,`server_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='项⽬服务器表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_service_info`
--

DROP TABLE IF EXISTS `project_service_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_service_info` (
  `project_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `service_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `system_type` char(32) DEFAULT NULL,
  `system_sub_type` char(32) DEFAULT NULL,
  `env_id` char(32) DEFAULT NULL,
  `server_id` char(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `service_port` int DEFAULT NULL,
  `service_protocol` char(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `remark` varchar(600) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`project_id`,`service_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='项⽬服务表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_service_list`
--

DROP TABLE IF EXISTS `project_service_list`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_service_list` (
  `project_id` char(20) NOT NULL,
  `service_id` char(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `service_type` char(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '01-CBS,02-Branch,03-Report,04-Peripheral,05-EBanking',
  `service_method` char(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT '01-socket,02-ssh',
  `service_name` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `service_ip` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `service_port` int DEFAULT NULL,
  `enabled` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Y-Enable,N-Disable',
  PRIMARY KEY (`project_id`,`service_type`,`service_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `project_service_log_path`
--

DROP TABLE IF EXISTS `project_service_log_path`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `project_service_log_path` (
  `project_id` char(20) NOT NULL,
  `service_id` char(20) NOT NULL,
  `log_path` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `enabled` char(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Y-Enable,N-Disable',
  PRIMARY KEY (`project_id`,`service_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `role_info`
--

DROP TABLE IF EXISTS `role_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_info` (
  `role_id` char(32) NOT NULL,
  `role_cn_name` varchar(600) DEFAULT NULL,
  `role_en_name` varchar(600) DEFAULT NULL,
  `menu_list` text,
  PRIMARY KEY (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduler_job`
--

DROP TABLE IF EXISTS `scheduler_job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scheduler_job` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '序号（自增主键）',
  `job_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL COMMENT '定时任务名称（唯一）',
  `script_name` varchar(200) COLLATE utf8mb4_general_ci NOT NULL COMMENT '脚本文件名（相对仓库路径，如 app/schedulerJob/pms_scheduler/jobs/task_analytical_status_job.py）',
  `description` varchar(500) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '脚本描述',
  `period_type` varchar(20) COLLATE utf8mb4_general_ci NOT NULL COMMENT '周期类型 second:秒 minute:分 hour:小时 day:天 week:周 month:月 quarter:季 year:年',
  `period_interval` int unsigned NOT NULL DEFAULT '1' COMMENT '周期间隔（配合 period_type，如 每2小时 = hour + interval 2）',
  `first_run_date` date DEFAULT NULL COMMENT '计划首次执行日期（配置项，与 first_run_time 组成首次执行时间点）',
  `first_run_time` time DEFAULT NULL COMMENT '计划首次执行时刻（配置项，如 06:30:00，当天该时刻首次触发）',
  `last_run_time` datetime DEFAULT NULL COMMENT '最近一次执行时间（任务回写，未执行为 NULL）',
  `last_run_date` date DEFAULT NULL COMMENT '最近一次执行日期（任务回写，按天粒度，判断当日是否已执行）',
  `last_run_status` tinyint NOT NULL DEFAULT '0' COMMENT '最近一次执行状态 0:未执行 1:成功 2:失败',
  `enabled` tinyint NOT NULL DEFAULT '1' COMMENT '启停 1:启用 0:停用',
  `log_level` varchar(10) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'INFO' COMMENT '脚本日志级别 DEBUG/INFO/WARNING/ERROR',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '创建人（登录账号）',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '更新人（登录账号）',
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '时间戳（数据库自动维护，插入/更新均刷新，外部不可写入）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_job_name` (`job_name`),
  UNIQUE KEY `uk_script_name` (`script_name`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='定时任务表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `scheduler_job_run_log`
--

DROP TABLE IF EXISTS `scheduler_job_run_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scheduler_job_run_log` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `job_id` bigint unsigned NOT NULL COMMENT 'scheduler_job.id',
  `script_name` varchar(200) COLLATE utf8mb4_general_ci NOT NULL COMMENT '脚本路径',
  `trigger_type` varchar(20) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'scheduled' COMMENT '触发方式 scheduled:定时 manual:手动',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT '0:运行中 1:成功 2:失败 3:超时',
  `start_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `pid` int DEFAULT NULL,
  `output` text COLLATE utf8mb4_general_ci COMMENT '脚本输出（尾部截断）',
  PRIMARY KEY (`id`),
  KEY `idx_job_id` (`job_id`),
  KEY `idx_start_time` (`start_time`)
) ENGINE=InnoDB AUTO_INCREMENT=598 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='定时任务运行日志';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `script_info`
--

DROP TABLE IF EXISTS `script_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `script_info` (
  `script_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL COMMENT '脚本名（主键）',
  `script_path` varchar(200) COLLATE utf8mb4_general_ci NOT NULL COMMENT '脚本路径（仓库相对路径，唯一）',
  `description` varchar(500) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '脚本描述',
  `params` json DEFAULT NULL COMMENT '脚本入参定义（JSON 数组，无入参存 []）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `create_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '创建人（登录账号）',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `update_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '更新人（登录账号）',
  `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '时间戳（数据库自动维护，插入/更新均刷新，外部不可写入）',
  PRIMARY KEY (`script_name`),
  UNIQUE KEY `uk_script_path` (`script_path`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='脚本信息表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_menu`
--

DROP TABLE IF EXISTS `sys_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_menu` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '菜单ID',
  `parent_id` bigint unsigned NOT NULL DEFAULT '0' COMMENT '父菜单ID，0=顶级',
  `menu_type` tinyint NOT NULL DEFAULT '2' COMMENT '类型 1:目录 2:菜单',
  `menu_name` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '菜单名称',
  `route_name` varchar(100) COLLATE utf8mb4_general_ci NOT NULL COMMENT '路由名称（前端 routeName，唯一）',
  `route_path` varchar(200) COLLATE utf8mb4_general_ci NOT NULL COMMENT '路由路径',
  `component` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '组件路径（目录为 NULL）',
  `icon` varchar(100) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '图标名',
  `icon_type` tinyint NOT NULL DEFAULT '1' COMMENT '图标类型 1:iconify 2:本地',
  `route_props` json DEFAULT NULL COMMENT '路由元信息（对应前端 MenuPropsOfRoute）',
  `buttons` json DEFAULT NULL COMMENT '按钮权限码 [{code,desc}]',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状态 1:启用 2:禁用',
  `create_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_route_name` (`route_name`),
  KEY `idx_parent_id` (`parent_id`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='菜单表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_refresh_token`
--

DROP TABLE IF EXISTS `sys_refresh_token`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_refresh_token` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint unsigned NOT NULL COMMENT '用户ID',
  `token_hash` char(64) COLLATE utf8mb4_general_ci NOT NULL COMMENT 'refreshToken 的 SHA-256 十六进制哈希',
  `expires_at` datetime NOT NULL COMMENT '过期时间',
  `revoked` tinyint NOT NULL DEFAULT '0' COMMENT '是否已吊销 0:否 1:是',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_token_hash` (`token_hash`),
  KEY `idx_user_id` (`user_id`),
  CONSTRAINT `fk_refresh_token_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=207 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='刷新令牌表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_role`
--

DROP TABLE IF EXISTS `sys_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_role` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `role_name` varchar(30) COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色名称',
  `role_code` varchar(50) COLLATE utf8mb4_general_ci NOT NULL COMMENT '角色编码（如 R_SUPER，前端 userRoles 存的就是它）',
  `role_desc` varchar(255) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '角色描述',
  `home` varchar(100) COLLATE utf8mb4_general_ci NOT NULL DEFAULT 'home' COMMENT '角色首页路由名',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状态 1:启用 2:禁用',
  `create_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_role_code` (`role_code`)
) ENGINE=InnoDB AUTO_INCREMENT=211 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='角色表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_role_button`
--

DROP TABLE IF EXISTS `sys_role_button`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_role_button` (
  `role_id` bigint unsigned NOT NULL COMMENT '角色ID',
  `menu_id` bigint unsigned NOT NULL COMMENT '菜单ID（按钮所属菜单）',
  `button_code` varchar(100) COLLATE utf8mb4_general_ci NOT NULL COMMENT '按钮权限码（如 B_USER::BTN_ADD）',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`,`menu_id`,`button_code`),
  KEY `idx_menu_id` (`menu_id`),
  CONSTRAINT `fk_role_button_menu` FOREIGN KEY (`menu_id`) REFERENCES `sys_menu` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_role_button_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='角色按钮权限表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_role_menu`
--

DROP TABLE IF EXISTS `sys_role_menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_role_menu` (
  `role_id` bigint unsigned NOT NULL,
  `menu_id` bigint unsigned NOT NULL,
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`role_id`,`menu_id`),
  KEY `idx_menu_id` (`menu_id`),
  CONSTRAINT `fk_role_menu_menu` FOREIGN KEY (`menu_id`) REFERENCES `sys_menu` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_role_menu_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='角色菜单关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_user`
--

DROP TABLE IF EXISTS `sys_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `user_name` varchar(30) COLLATE utf8mb4_general_ci NOT NULL COMMENT '用户名（登录账号，唯一）',
  `password` varchar(100) COLLATE utf8mb4_general_ci NOT NULL COMMENT '密码哈希（bcrypt，永不返回给前端）',
  `user_gender` tinyint DEFAULT NULL COMMENT '性别 1:男 2:女 NULL:未设置',
  `nick_name` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '昵称',
  `user_phone` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '手机号（空须存 NULL 而不是空串，否则唯一索引冲突）',
  `user_email` varchar(100) COLLATE utf8mb4_general_ci DEFAULT NULL COMMENT '邮箱（同上）',
  `status` tinyint NOT NULL DEFAULT '1' COMMENT '状态 1:启用 2:禁用（登录时校验）',
  `create_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '创建人',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_by` varchar(30) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '更新人',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_name` (`user_name`),
  UNIQUE KEY `uk_user_phone` (`user_phone`),
  UNIQUE KEY `uk_user_email` (`user_email`)
) ENGINE=InnoDB AUTO_INCREMENT=209 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sys_user_role`
--

DROP TABLE IF EXISTS `sys_user_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sys_user_role` (
  `user_id` bigint unsigned NOT NULL COMMENT '用户ID',
  `role_id` bigint unsigned NOT NULL COMMENT '角色ID',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `idx_role_id` (`role_id`),
  CONSTRAINT `fk_user_role_role` FOREIGN KEY (`role_id`) REFERENCES `sys_role` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_user_role_user` FOREIGN KEY (`user_id`) REFERENCES `sys_user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='用户角色关联表';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `task_monitor_daily_stat`
--

DROP TABLE IF EXISTS `task_monitor_daily_stat`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `task_monitor_daily_stat` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `stat_date` date NOT NULL COMMENT '统计日期',
  `member` varchar(30) COLLATE utf8mb4_general_ci NOT NULL COMMENT '成员名字',
  `project_id` int unsigned NOT NULL DEFAULT '0' COMMENT '项目ID',
  `team` varchar(50) COLLATE utf8mb4_general_ci NOT NULL DEFAULT '' COMMENT '所属团队',
  `completed_today_count` int NOT NULL DEFAULT '0' COMMENT '今日完成任务数',
  `overdue_count` int NOT NULL DEFAULT '0' COMMENT '今日逾期任务数（到期日=统计日）',
  `uncomplete_today_count` int NOT NULL DEFAULT '0' COMMENT '今日未完成任务数',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `completed_today_list` json DEFAULT NULL COMMENT '今日完成任务清单 JSON',
  `overdue_list` json DEFAULT NULL COMMENT '今日逾期任务清单 JSON',
  `uncomplete_today_list` json DEFAULT NULL COMMENT '今日未完成任务清单 JSON',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_date_member_project` (`stat_date`,`member`,`project_id`),
  KEY `idx_team_date` (`team`,`stat_date`)
) ENGINE=InnoDB AUTO_INCREMENT=1020 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='成员任务监控每日快照（每成员每天一条）';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user_info`
--

DROP TABLE IF EXISTS `user_info`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_info` (
  `user_id` char(60) NOT NULL,
  `user_name` char(255) DEFAULT NULL,
  `phone` char(20) DEFAULT NULL,
  `mail` char(120) DEFAULT NULL,
  `role_id` char(30) DEFAULT NULL,
  `project_list` varchar(600) DEFAULT NULL,
  `user_password` varchar(600) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  `current_project` char(32) DEFAULT NULL,
  `current_token` char(32) DEFAULT NULL,
  `token_expire_time` datetime DEFAULT NULL,
  PRIMARY KEY (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping events for database 'oms'
--

--
-- Dumping routines for database 'oms'
--
--
-- WARNING: can't read the INFORMATION_SCHEMA.libraries table. It's most probably an old server 9.1.0.
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-10-24 12:37:01
