import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from util import *

SMALL_SIZE = 5.5
MEDIUM_SIZE = 9
BIGGER_SIZE = 11

plt.switch_backend('agg')
plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=SMALL_SIZE)     # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
plt.rc('axes', linewidth=0.5)            # set the value globally
plt.rc('xtick.major', width=0.5)         # set the value globally
plt.rc('ytick.major', width=0.5)         # set the value globally
plt.rc('lines', linewidth=1)             # line thickness
plt.rc('ytick.major', size=2)            # set the value globally
plt.rc('xtick.major', size=2)            # set the value globally
plt.rc('text', usetex=True)
plt.rc('text.latex',
       preamble=[r'\usepackage{amsmath}',
                 r'\usepackage[cm]{sfmath}'])  # for \text command
plt.rc('font', **{'family': 'sans-serif', 'sans-serif': ['cm']})


def main():
    seeds = np.arange(1, 11, dtype=int)
    uids = ['3319b6a9', '03ee5995', '179b8125', '871c4fce']
    concrete_uids = ['eaf03c8b', '7da5406d', '2c000794', '5b1962a9']
    reinforce_uids = ['9b28ea68', 'f6ebee25', 'e520c68c', '4c1be354']
    relax_uids = ['e24618b3', 'a91304d3', 'a3dfe440', '3b3475dc']
    num_particles = [2, 5, 10, 20]
    ww_probs = [1.0, 0.8]

    num_iterations = np.load('{}/num_iterations_{}.npy'.format(WORKING_DIR, uids[0]))
    logging_interval = np.load('{}/logging_interval_{}.npy'.format(WORKING_DIR, uids[0]))
    logging_iterations = np.arange(0, num_iterations, logging_interval)

    # Plotting
    fig, axs = plt.subplots(3, len(uids), sharex=True, sharey='row')
    fig.set_size_inches(5.5, 3)

    for ax_idx in range(len(uids)):
        uid = uids[ax_idx]
        concrete_uid = concrete_uids[ax_idx]
        reinforce_uid = reinforce_uids[ax_idx]
        relax_uid = relax_uids[ax_idx]

        iwae_filenames = ['p_mixture_probs_norm_history', 'true_posterior_norm_history', 'q_grad_std_history']
        rws_filenames = ['p_mixture_probs_norm_history', 'true_posterior_norm_history', 'q_grad_std_history']
        concrete_names = ['prior_l2_history', 'true_posterior_l2_history', 'inference_network_grad_phi_std_history']
        relax_names = concrete_names

        # Concrete
        concrete = read_files('concrete', concrete_names, seeds, concrete_uid)
        kwargs = {'linestyle': '--', 'label': 'Concrete', 'color': 'C0'}

        for idx, name in enumerate(concrete_names):
            plot_with_error_bars(logging_iterations, concrete[name], axs[idx, ax_idx], **kwargs)

        # Relax
        # if ax_idx == 0:
        relax = read_files('relax', relax_names, seeds, relax_uid)
        kwargs = {'linestyle': '--', 'label': 'RELAX', 'color': 'C3'}

        for idx, name in enumerate(relax_names):
            plot_with_error_bars(logging_iterations, relax[name], axs[idx, ax_idx], **kwargs)
            # print(relax[name][0])
            # axs[idx, ax_idx].plot(logging_iterations, relax[name][0], **kwargs)

        ## IWAE
        # Reinforce
        iwae_reinforce = read_files('iwae_reinforce', iwae_filenames, seeds, reinforce_uid)
        kwargs = {'linestyle': '--', 'label': 'REINFORCE', 'color': 'C4'}

        for idx, filename in enumerate(iwae_filenames):
            plot_with_error_bars(logging_iterations, iwae_reinforce[filename], axs[idx, ax_idx], **kwargs)

        # VIMCO
        iwae_vimco = read_files('iwae_vimco', iwae_filenames, seeds, uid)
        kwargs = {'linestyle': '--', 'label': 'VIMCO', 'color': 'C5'}

        for idx, filename in enumerate(iwae_filenames):
            plot_with_error_bars(logging_iterations, iwae_vimco[filename], axs[idx, ax_idx], **kwargs)

        # WS
        ws = read_files('ws', rws_filenames , seeds, uid)
        kwargs = {'linestyle': '-', 'label': 'WS', 'color': 'C1'}

        for idx, filename in enumerate(rws_filenames):
            plot_with_error_bars(logging_iterations, ws[filename], axs[idx, ax_idx], **kwargs)

        # WW
        for q_mixture_prob_idx, q_mixture_prob in enumerate(ww_probs):
            ww = read_files('ww_{}'.format(str(q_mixture_prob).replace('.', '-')), rws_filenames, seeds, uid)
            kwargs = {'linestyle': '-', 'label': '{}'.format('WW' if q_mixture_prob == 1 else r'$\delta$-WW'), 'color': 'C{}'.format(q_mixture_prob_idx + 6)}

            for idx, filename in enumerate(iwae_filenames):
                plot_with_error_bars(logging_iterations, ww[filename], axs[idx, ax_idx], **kwargs)



    axs[0, 0].set_yscale('log')
    axs[0, 0].set_ylabel(r'$\| p_{\theta}(z) - p_{\theta_{\text{true}}}(z) \|$')

    axs[1, 0].set_yscale('log')
    axs[1, 0].set_ylabel('Avg. test\n' + r'$\| q_\phi(z | x) - p_{\theta_{\text{true}}}(z | x) \|$')

    axs[2, 0].set_yscale('log')
    axs[2, 0].set_ylabel('Std. of $\phi$ \n gradient est.')

    axs[-1, 1].legend(ncol=7, loc='upper center', bbox_to_anchor=(1, -0.2))
    for i, ax in enumerate(axs[0]):
        ax.set_title('$K = {}$'.format(num_particles[i]))
    for i, ax in enumerate(axs[-1]):
        ax.set_xlabel('Iteration')
        ax.xaxis.set_label_coords(0.5, -0.1)

    for axss in axs:
        for ax in axss:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.minorticks_off()
            ax.set_xticks([0, 100000])

    fig.tight_layout(pad=0)
    filename = 'results/plot_paper.pdf'
    fig.savefig(filename, bbox_inches='tight')
    print('Saved to {}'.format(filename))


def read_files(algorithm, filenames, seeds, uid):
    num_seeds = len(seeds)
    temp = np.load('{}/{}_{}_{}_{}.npy'.format(WORKING_DIR, algorithm, filenames[0], seeds[0], uid))
    num_data = len(temp)
    result = {}
    for filename in filenames:
        result[filename] = np.zeros([num_seeds, num_data])
        for seed_idx, seed in enumerate(seeds):
            result[filename][seed_idx] = np.load('{}/{}_{}_{}_{}.npy'.format(
                WORKING_DIR, algorithm, filename, seed, uid
            ))
    return result


def plot_with_error_bars(x, ys, ax, *args, **kwargs):
    median = np.median(ys, axis=0)
    first_quartile = np.percentile(ys, 25, axis=0)
    third_quartile = np.percentile(ys, 75, axis=0)
    line = ax.plot(x, median, *args, **kwargs)
    ax.fill_between(x, y1=first_quartile, y2=third_quartile, alpha=0.2, color=line[0].get_color())
    return ax


if __name__ == '__main__':
    main()