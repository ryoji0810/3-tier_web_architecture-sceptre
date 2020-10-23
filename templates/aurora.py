from base import Base

from troposphere_mate import (
    rds,
    Ref,
)


class Aurora(Base):
    # security_group.yamlから変数を取得する(11~43行)
    @property
    def prefix(self):
        return self.sceptre_user_data['prefix']

    @property
    def project(self):
        return self.sceptre_user_data['project']

    @property
    def deletion_protection(self):
        return self.sceptre_user_data['deletion_protection']

    @property
    def cluster_class(self):
        return self.sceptre_user_data['cluster_class']

    @property
    def cluster_password(self):
        return self.sceptre_user_data['cluster_password']

    @property
    def db_subnet_id_list(self):
        val = []
        for v in self.sceptre_user_data['db_subnet_id_list']:
            val.extend(v.split(','))
        return val

    @property
    def db_sg_list(self):
        val = []
        for v in self.sceptre_user_data['db_sg_list']:
            val.extend(v.split(','))
        return val

    def create_template(self):
        # クラスターのパラメータグループを作成
        db_cluster_parameter_group = self.tpl.add_resource(
            rds.DBClusterParameterGroup(
                'DBClusterParams',
                Description=f'{self.prefix}-{self.project}-db-cluster-parameters',
                Family='aurora-mysql5.7',
                Parameters={
                    'time_zone': 'Asia/Tokyo',
                    'character_set_client': 'utf8mb4',
                    'character_set_connection': 'utf8mb4',
                    'character_set_database': 'utf8mb4',
                    'character_set_results': 'utf8mb4',
                    'character_set_server': 'utf8mb4',
                    'default_password_lifetime': '0',
                }
            )
        )

        # サブネットグループを作成
        db_subnet_group = self.tpl.add_resource(
            rds.DBSubnetGroup(
                'DBSubnetGroup',
                DBSubnetGroupDescription=f'{self.prefix}-{self.project}-subnet-group',
                SubnetIds=self.db_subnet_id_list
            )
        )

        # サブネットグループを作成
        cluster = self.tpl.add_resource(
            rds.DBCluster(
                'AuroraCluster',
                BacktrackWindow=72,
                BackupRetentionPeriod=7,
                DBClusterParameterGroupName=Ref(db_cluster_parameter_group),
                DBSubnetGroupName=Ref(db_subnet_group),
                DeletionProtection=self.deletion_protection,
                Engine='aurora-mysql',
                EngineMode='provisioned',
                EngineVersion='5.7.mysql_aurora.2.08.2',
                MasterUsername='admin',
                MasterUserPassword=self.cluster_password,
                PreferredMaintenanceWindow='Fri:14:29-Fri:14:59',
                StorageEncrypted=True,
                VpcSecurityGroupIds=self.db_sg_list,
            )
        )

        # DBインスタンスのパラメータグループを作成
        db_parameter_group = self.tpl.add_resource(
            rds.DBParameterGroup(
                'DBParameterGroup',
                Description=f'{self.prefix}-{self.project}-db-parameters',
                Family='aurora-mysql5.7'
            )
        )

        # DBインスタンスを作成
        self.tpl.add_resource(
            rds.DBInstance(
                'AuroraInstance',
                AllowMajorVersionUpgrade=False,
                AutoMinorVersionUpgrade=False,
                DBClusterIdentifier=Ref(cluster),
                DBInstanceClass=self.cluster_class,
                DBSubnetGroupName=Ref(db_subnet_group),
                DeleteAutomatedBackups=False,
                Engine='aurora-mysql',
                DBParameterGroupName=Ref(db_parameter_group),
                PubliclyAccessible=False
            )
        )


# SceptreにTemplateを渡してCFnを実行する
def sceptre_handler(sceptre_user_data):
    return Aurora(sceptre_user_data).to_yaml()
