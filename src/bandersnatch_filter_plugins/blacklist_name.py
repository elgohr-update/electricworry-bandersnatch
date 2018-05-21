import logging
from bandersnatch.filter import FilterProjectPlugin, FilterReleasePlugin
from packaging.requirements import Requirement


logger = logging.getLogger(__name__)


class BlacklistProject(FilterProjectPlugin):
    name = 'blacklist_project'

    def initialize_plugin(self):
        """
        Initialize the plugin
        """
        # Generate a list of blacklisted packages from the configuration and
        # store it into self.blacklist_package_names attribute so this
        # operation doesn't end up in the fastpath.
        logger.debug('Initializing the %r plugin', self.name)
        self.blacklist_package_names = self._determine_filtered_package_names()

    def _determine_filtered_package_names(self):
        """
        Return a list of package names to be filtered base on the configuration
        file.
        """
        # This plugin only processes packages, if the line in the packages
        # configuration contains a PEP440 specifier it will be processed by the
        # blacklist release filter.  So we need to remove any packages that
        # are not applicable for this plugin.
        filtered_packages = set()
        try:
            lines = self.configuration['blacklist']['packages']
            logger.debug('blacklist->packages: %r', lines)
            package_lines = lines.split('\n')
        except KeyError:
            package_lines = []
        for package_line in package_lines:
            package_line = package_line.strip()
            if not package_line:
                continue
            package_requirement = Requirement(package_line)
            if package_requirement.specifier:
                logger.debug(
                    'Package line %r has a version spec, ignoring',
                    package_line
                )
                continue
            if package_requirement.name != package_line:
                logger.debug(
                    'Package line %r does not requirement name %r',
                    package_line, package_requirement.name
                )
                continue
            filtered_packages.add(package_line)
        logger.debug('Project blacklist is %r', list(filtered_packages))
        return list(filtered_packages)

    def check_match(self, **kwargs):
        """
        Check if the package name matches against a project that is blacklisted
        in the configuration.

        Parameters
        ==========
        name: str
            The normalized package name of the package/project to check against
            the blacklist.

        Returns
        =======
        bool:
            True if it matches, False otherwise.
        """
        logger.debug('Running filter plugin %s', self.name)
        name = kwargs.get('name', None)
        if not name:
            return False

        logger.info(
            'Checking for package %s in %r', name, self.blacklist_package_names
        )
        if name in self.blacklist_package_names:
            logger.debug(
                'MATCH: Package %r is in %r', name,
                self.blacklist_package_names
            )
            return True
        return False


class BlacklistRelease(FilterReleasePlugin):
    name = 'blacklist_release'

    def check_match(self, **kwargs):
        """
        Check if the package name  and version matches against a blacklisted
        package version specifier.

        Parameters
        ==========
        name: str
            Package name

        version: str
            Package version

        Returns
        =======
        bool:
            True if it matches, False otherwise.
        """
        name = kwargs.get('name', None)
        version = kwargs.get('version', None)

        if not name or not version:
            return False

        return False