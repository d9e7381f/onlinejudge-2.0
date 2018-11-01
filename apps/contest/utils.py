import ipaddress


def is_competitor(contest, user, request=None):
    """Whether a user is a competitor of a contest."""
    # Anonymous user is always not a competitor.
    if user.is_anonymous:
        return False
    # Admin always is competitor.
    elif user.is_admin_role():
        return True

    # Regular user can't retrieve invisible contest.
    if not contest.visible:
        return False

    # True if no group and no IP limitation.
    if not contest.groups.exists() and not contest.allowed_ip_ranges:
        return True
    else:
        # Check if user in the contest groups list.
        if contest.groups.exists() \
           and not contest.groups \
                          .filter(pk=user.userprofile.group.pk) \
                          .exists():
            return False

        # Check if user request IP in allowed IP ranges.
        if contest.allowed_ip_ranges:
            # request is required to get the IP.
            if not request:
                print('request is required')
                return False
            else:
                request_ip = ipaddress.ip_address(request.ip)
                if not any(
                    request_ip in ipaddress.ip_network(cidr, strict=False)
                    for cidr in contest.allowed_ip_ranges
                ):
                    return False

        # True if pass all check.
        return True
