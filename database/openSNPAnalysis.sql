SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL';

CREATE SCHEMA IF NOT EXISTS `openSNPAnalysis` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci ;
USE `openSNPAnalysis` ;

-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`phenotype`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`phenotype` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`phenotype` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(100) NOT NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_bin;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`user` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`user` (
  `id` INT NOT NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`phenotype_value`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`phenotype_value` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`phenotype_value` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `id_pheno` INT NOT NULL ,
  `value` VARCHAR(400) NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `pheno_pheno_value` (`id_pheno` ASC) ,
  CONSTRAINT `pheno_pheno_value`
    FOREIGN KEY (`id_pheno` )
    REFERENCES `openSNPAnalysis`.`phenotype` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`pheno_user`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`pheno_user` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`pheno_user` (
  `id_pheno` INT NOT NULL ,
  `id_user` INT NOT NULL ,
  `id_phenotype_value` INT NOT NULL ,
  INDEX `pheno_pheno_f` (`id_pheno` ASC) ,
  INDEX `pheno_user_f` (`id_user` ASC) ,
  PRIMARY KEY (`id_pheno`, `id_user`) ,
  INDEX `pheno_value_f` (`id_phenotype_value` ASC) ,
  CONSTRAINT `pheno_pheno_f`
    FOREIGN KEY (`id_pheno` )
    REFERENCES `openSNPAnalysis`.`phenotype` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `pheno_user_f`
    FOREIGN KEY (`id_user` )
    REFERENCES `openSNPAnalysis`.`user` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `pheno_value_f`
    FOREIGN KEY (`id_phenotype_value` )
    REFERENCES `openSNPAnalysis`.`phenotype_value` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`snp`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`snp` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`snp` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(45) NOT NULL ,
  `chromosome` INT NOT NULL ,
  `location` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`allele`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`allele` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`allele` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `allele1` CHAR NOT NULL ,
  `allele2` CHAR NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`geno_method`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`geno_method` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`geno_method` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `name` VARCHAR(45) NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`genotype_file`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`genotype_file` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`genotype_file` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `filename` VARCHAR(45) NOT NULL ,
  `id_user` INT NOT NULL ,
  `id_method` INT NOT NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `file_user` (`id_user` ASC) ,
  INDEX `file_method` (`id_method` ASC) ,
  CONSTRAINT `file_user`
    FOREIGN KEY (`id_user` )
    REFERENCES `openSNPAnalysis`.`user` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `file_method`
    FOREIGN KEY (`id_method` )
    REFERENCES `openSNPAnalysis`.`geno_method` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`genotype`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`genotype` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`genotype` (
  `id_snp` INT NOT NULL ,
  `id_allele` INT NOT NULL ,
  `id_genotype_file` INT NOT NULL ,
  PRIMARY KEY (`id_snp`, `id_allele`, `id_genotype_file`) ,
  INDEX `geno_snp` (`id_snp` ASC) ,
  INDEX `geno_allele` (`id_allele` ASC) ,
  INDEX `geno_geno_file` (`id_genotype_file` ASC) ,
  CONSTRAINT `geno_snp`
    FOREIGN KEY (`id_snp` )
    REFERENCES `openSNPAnalysis`.`snp` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `geno_allele`
    FOREIGN KEY (`id_allele` )
    REFERENCES `openSNPAnalysis`.`allele` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `geno_geno_file`
    FOREIGN KEY (`id_genotype_file` )
    REFERENCES `openSNPAnalysis`.`genotype_file` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`paper`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`paper` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`paper` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `doi` VARCHAR(45) NULL ,
  `title` VARCHAR(500) NULL ,
  `authors` VARCHAR(500) NULL ,
  `pubmed_id` VARCHAR(45) NULL ,
  `year` INT NULL ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`snp_paper`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`snp_paper` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`snp_paper` (
  `id_paper` INT NOT NULL ,
  `id_snp` INT NOT NULL ,
  PRIMARY KEY (`id_paper`, `id_snp`) ,
  INDEX `snp_paper_paper` (`id_paper` ASC) ,
  INDEX `snp_paper_snp` (`id_snp` ASC) ,
  CONSTRAINT `snp_paper_paper`
    FOREIGN KEY (`id_paper` )
    REFERENCES `openSNPAnalysis`.`paper` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `snp_paper_snp`
    FOREIGN KEY (`id_snp` )
    REFERENCES `openSNPAnalysis`.`snp` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `openSNPAnalysis`.`snpedia`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `openSNPAnalysis`.`snpedia` ;

CREATE  TABLE IF NOT EXISTS `openSNPAnalysis`.`snpedia` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `id_snp` INT NOT NULL ,
  `id_allele` INT NOT NULL ,
  `summary` VARCHAR(200) NULL ,
  PRIMARY KEY (`id`) ,
  INDEX `snpedia_snp` (`id_snp` ASC) ,
  INDEX `snpedia_allele` (`id_allele` ASC) ,
  CONSTRAINT `snpedia_snp`
    FOREIGN KEY (`id_snp` )
    REFERENCES `openSNPAnalysis`.`snp` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `snpedia_allele`
    FOREIGN KEY (`id_allele` )
    REFERENCES `openSNPAnalysis`.`allele` (`id` )
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;



SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
